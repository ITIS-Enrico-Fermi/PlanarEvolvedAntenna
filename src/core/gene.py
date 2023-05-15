import logging
import numpy as np
from necpp import *
from config import Config
from utils.geometry import *
from rf.radiation import RadiationPattern, RpCardEvaluationInput
from rf.nec_analysis import NecAnalysis

class Gene:
  globalSerial = 0
  GAIN_K = 1
  STANDARD_DEVIATION_K = 0
  # STANDARD_DEVIATION_K = -1  # Penalize high sd

  def __init__(self, rodEncodedGene: List[PolarCoord] = None):
    self.FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)

    self.radiationPattern = None
    self.fitnessCached = float("-inf")
    self.groundPlaneDistance = Config.ShapeConstraints.groundPlaneDistance

    self.serial = Gene.globalSerial
    Gene.globalSerial += 1

    if (rodEncodedGene is not None):
      self.rodEncoding = rodEncodedGene
      self.polychainEncoding = polarToPolychain(
        self.FIRST_POINT,
        rodToPolar(self.rodEncoding)
      )
      return

    revolutionAngles = (np.random.rand(Config.GeneEncoding.segmentsNumber) - 0.5) * \
      Config.GeneEncoding.maxAngle
    
    segmentLengths = np.random.uniform(
      low = Config.GeneEncoding.minSegmentLen,
      high = Config.GeneEncoding.maxSegmentLen,
      size = Config.GeneEncoding.segmentsNumber)

    self.setEncoding(revolutionAngles, segmentLengths)

  def __lt__(self, other) -> bool:
    return self.fitness() < other.fitness()
  
  def __repr__(self) -> str:
    res = f"GeneID: {self.serial} <"

    lastItemIdx = len(self.rodEncoding) - 1

    for i in range(lastItemIdx):
      res += f"{self.rodEncoding[i].angle:.1f} deg - {self.rodEncoding[i].distance:.1f} mm - "
    res += f"{self.rodEncoding[lastItemIdx].angle:.1f} deg - {self.rodEncoding[lastItemIdx].distance:.1f} mm>"

    return res
  
  def __getitem__(self, itemIdx):
    return self.rodEncoding[itemIdx]
  
  def getPolarCoords(self) -> List[PolarCoord]:
    return self.rodEncoding

  def getCartesianCoords(self) -> List[Segment]:
    return self.polychainEncoding
  
  def getAngleArray(self) -> np.ndarray:
    return np.asarray(
      list(zip(*self.rodEncoding))[0]
    )

  def getLengthArray(self) -> np.ndarray:
    return np.asarray(
      list(zip(*self.rodEncoding))[1]
    )

  def getRadiationPattern(self) -> RadiationPattern:
    return self.radiationPattern
  
  def setEncoding(self, angles: List[float], lengths: List[float]) -> None:
    self.rodEncoding = list(zip(angles, lengths))
    self.rodEncoding = [PolarCoord(a, l) for (a, l) in self.rodEncoding]

    self.polychainEncoding = polarToPolychain(
        self.FIRST_POINT,
        rodToPolar(self.rodEncoding)
      )

  def isValid(self) -> bool:
    """Returns true if the path is not slef-intersecting
    and doesn't come across the inner hole
    """
    OUTER_RADIUS = Config.ShapeConstraints.outerDiam / 2
    INNER_RADIUS = Config.ShapeConstraints.innerDiam / 2
    
    return (
      not isSelfIntersectingPath(self.polychainEncoding) and
      not doesPathIntersectCircle(self.polychainEncoding, Point(Config.ShapeConstraints.centerShift, 0), INNER_RADIUS) and
      isPathInCircle(self.polychainEncoding, Point(0, 0), OUTER_RADIUS)
    )

  def fitness(self) -> np.float16:
    freqHz = Config.ShapeConstraints.targetFreq

    try:
      with NecAnalysis(self, freqHz) as sim:
        context = sim.getNecContext()

        sim.addInfiniteGroundPlane()
        sim.runExcitation()
        self.radiationPattern = sim.computeRadiationPattern([
          RpCardEvaluationInput(60, 0, -9, 0, 0, 0),
          RpCardEvaluationInput(15, 60, 9, 180, 180, 0),
          RpCardEvaluationInput(60, 0, -9, 90, 90, 0),
          RpCardEvaluationInput(15, 60, 9, 270, 270, 0)
        ])

        self.fitnessCached = \
          self.GAIN_K * nec_gain_min(context, 0) + \
          self.STANDARD_DEVIATION_K * nec_gain_sd(context, 0)
        
        logging.debug(
          f"Gain\n"
          f"\tmin: {nec_gain_min(context, 0)}\n"
          f"\tmax: {nec_gain_max(context, 0)}\n"
          f"\tmean: {nec_gain_mean(context, 0)}\n"
          f"\tsd: {nec_gain_sd(context, 0)}\n"
        )

    except AssertionError:
      self.fitnessCached = float("-inf")  # This gene will be discarded at the next iteration

    finally:
      return self.fitnessCached

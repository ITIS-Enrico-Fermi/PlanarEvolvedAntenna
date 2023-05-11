import logging
import math
import numpy as np
from typing import List, Tuple
from necpp import *
from config import Config
from utils.geometry import *
from rf.antenna_util import *
from rf.context_clean import *


class Gene:
  globalSerial: int = 0

  def __init__(self, rodEncodedGene: List[PolarCoord] = None):
    self.FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)
    self.fitnessCached = float("-inf")
    self.ampK = None
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
  
  def ampFactor(self, x: float):
    if self.ampK is None:
      self.ampK = ampK = math.exp(-0.002 * (x - 400)) - 1
    
    logging.debug(f"ampK: {self.ampK}")
    return self.ampK

  def fitness(self) -> np.float16:
    SUBSTRATE_THICKNESS = 2
    freqHz = Config.ShapeConstraints.targetFreq
    wavelength = 299792e3 / freqHz
    context = nec_create()

    for segment in self.getCartesianCoords():
      assert nec_wire(
        context,
        self.globalSerial,  # tag ID
        1,  # Segment count
        segment.start.x / 1000,  # Start point x in m
        segment.start.y / 1000,  # Start point y in m
        SUBSTRATE_THICKNESS / 1000,  # Start point z in m
        segment.end.x / 1000,  # Start point x in m
        segment.end.y / 1000,  # Start point y in m
        SUBSTRATE_THICKNESS / 1000, # Start point z in m
        0.0001,  # First segment radius
        1,  # Uniform length
        1  # Ratio of adjacent segments
      ) == 0

    assert nec_geometry_complete(context, 0) == 0  # inner 0 means no ground-plane
    assert nec_gn_card(context, 1, 0, 0, 0, 0, 0, 0, 0) == 0  # Infinite ground plane
    
    assert nec_fr_card(  # Frequency
      context,
      0,  # Linear range
      1,  # One frequency
      freqHz / 1e6,  # Frequency in MHz
      0  # Frequency step
    ) == 0

    assert nec_ex_card(  # Excitatoin
      context,
      0,  # Voltage source excitation
      self.globalSerial,  # Tag number (from source segment)
      1,  # N-th segment of the source set of segments
      0,
      1.0, 0, 0, 0, 0, 0  # Tmp
    ) == 0

    assert nec_rp_card(  # Radiation Pattern
      context,
      0,  # Normal calc mode
      12,  # Number of theta angles
      1,  # Number of phi angles
      0,  # Major-minor axes
      5,  # Total gain normalized
      0,  # Power gain
      0,  # Do averaging
      0,  # Theta zero
      90,  # Phi zero
      15,  # Theta increment in deg
      0,  # Phi increment in deg
      0,  # Radial distance from origin
      0,  # Normalization factor
    ) == 0

    self.fitnessCached = nec_gain_max(context, 0) + self.ampFactor(nec_gain_sd(context, 0))
    logging.debug(f"Gain\n"
                 f"\tmin: {nec_gain_min(context, 0)}\n"
                 f"\tmax: {nec_gain_max(context, 0)}\n"
                 f"\tmean: {nec_gain_mean(context, 0)}\n"
                 f"\tsd: {nec_gain_sd(context, 0)}\n"
                 )

    nec_delete(context)

    return self.fitnessCached

    

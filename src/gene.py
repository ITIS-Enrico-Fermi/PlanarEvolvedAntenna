import numpy as np
from typing import List, Tuple
from utils import *
from config import Config


class Gene:
  serial: int = 0

  def __init__(self, rodEncodedGene: List[PolarCoord] = None):
    self.FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)

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

    self.serial = Gene.serial
    Gene.serial += 1

  def __lt__(self, other) -> bool:
    return self.fitness() < other.fitness()
  
  def __repr__(self) -> str:
    res = f"{self.serial} <"
    lastItemIdx = len(self.rodEncoding) - 1
    for i in range(lastItemIdx):
      res += f"{self.rodEncoding[i].angle} deg - {self.rodEncoding[i].distance} mm - "
    res += f"{self.rodEncoding[lastItemIdx].angle} deg - {self.rodEncoding[lastItemIdx].distance} mm>"

    return res
  
  def __getitem__(self, itemIdx):
    return self.rodEncoding[itemIdx]
  
  def getPolarCoords(self) -> List[PolarCoord]:
    return self.rodEncoding
  
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
  
  def fitness(self) -> np.float16:
    return 1

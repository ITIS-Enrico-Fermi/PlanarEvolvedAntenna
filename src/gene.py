import numpy as np
from typing import List, Tuple
from utils import PolarCoord
from config import Config


class Gene:
  serial: int = 0

  def __init__(self, encodedGene: List[PolarCoord] = None):
    if (encodedGene is not None):
      self.encoding = encodedGene
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
    lastItemIdx = len(self.encoding) - 1
    for i in range(lastItemIdx):
      res += f"{self.encoding[i].angle} deg - {self.encoding[i].distance} mm - "
    res += f"{self.encoding[lastItemIdx].angle} deg - {self.encoding[lastItemIdx].distance} mm>"

    return res
  
  def __getitem__(self, itemIdx):
    return self.encoding[itemIdx]
  
  def getPolarCoords(self) -> List[PolarCoord]:
    return self.encoding
  
  def getAngleArray(self) -> np.ndarray:
    return np.asarray(
      list(zip(*self.encoding))[0]
    )

  def getLengthArray(self) -> np.ndarray:
    return np.asarray(
      list(zip(*self.encoding))[1]
    )
  
  def setEncoding(self, angles: List[float], lengths: List[float]) -> None:
    self.encoding = list(zip(angles, lengths))
    self.encoding = [PolarCoord(a, l) for (a, l) in self.encoding]

  def isValid(self) -> bool:
    """Returns true if the path is not slef-intersecting
    and doesn't come across the inner hole
    """
    return True
  
  def fitness(self) -> np.float16:
    return 1

import matplotlib
import numpy as np
from typing import List

POP_SIZE  = 100

ITERATIONS_NUMBER = 10^3
SEGMENTS_NUMBER = 5

CUT_POINTS = 1
MUTATION_RATE = 0.3

OUTER_DIAM = 66  # < mm
INNER_DIAM = 7  # < mm
CENTER_SHIFT = 5.6  # < mm

class Gene:
  def __init__(self):
    self.segmentLengths = np.random.rand(SEGMENTS_NUMBER)  * OUTER_DIAM / (SEGMENTS_NUMBER * 4)
    self.revolutionAngles = np.random.rand(SEGMENTS_NUMBER - 1) * np.pi # 1 joint every segments' couple
    self.originTranslation = 0

  def isValid(self) -> bool:
    """Returns true if the path is not slef-intersecting
    and doesn't come across the inner hole
    """
    ...
  
  def fitness(self) -> np.float16:
    ...


class Generation:
  def __init__(self):
    self.genes = [Gene() for _ in range(POP_SIZE)]

  def iterate(self) -> List[Gene]:
    for _ in range(ITERATIONS_NUMBER):
      self.fight()
      self.crossover()
      self.mutate()
      yield self.genes

def main():
  ...

if __name__ == "__main__":
  main()
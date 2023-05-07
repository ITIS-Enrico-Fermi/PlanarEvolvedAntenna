from config import Config
import numpy as np
from typing import List

class Gene:
  def __init__(self):
    self.segmentLengths = np.random.rand(Config.GeneEncoding.segmentsNumber)  * Config.ShapeConstraints.outerDiam / (Config.GeneEncoding.segmentsNumber * 4)
    self.revolutionAngles = np.random.rand(Config.GeneEncoding.segmentsNumber - 1) * np.pi # 1 joint every segments' couple

  def isValid(self) -> bool:
    """Returns true if the path is not slef-intersecting
    and doesn't come across the inner hole
    """
    ...
  
  def fitness(self) -> np.float16:
    ...


class Generation:
  def __init__(self):
    self.population = [Gene() for _ in range(Config.GeneticAlgoTuning.populationSize)]

  def iterate(self) -> List[Gene]:
    for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
      self.fight()
      self.crossover()
      self.mutate()
      yield self.population


def main():
  ...


if __name__ == "__main__":
  main()
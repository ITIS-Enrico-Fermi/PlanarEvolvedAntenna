import numpy as np
from random import randrange
from config import Config
from typing import List

CONFIG_FILENAME = "config.yaml"

class Gene:
  def __init__(self):
    self.segmentLengths = \
      np.random.rand(Config.GeneEncoding.segmentsNumber)  * \
      Config.ShapeConstraints.outerDiam / (Config.GeneEncoding.segmentsNumber * 4)
    
    self.revolutionAngles = \
      (np.random.rand(Config.GeneEncoding.segmentsNumber - 1) - 0.5) * np.pi # 1 joint every segments' couple

  def __lt__(self, other) -> bool:
    return self.fitness() < other.fitness()
  
  def __repr__(self) -> str:
    res = ""
    for i in range(1, self.revolutionAngles.size):
      res += f"{self.segmentLengths[i-1]} mm - {self.revolutionAngles[i]} deg - "
    res += f"{self.segmentLengths[i-1]} mm"

    return res

  def isValid(self) -> bool:
    """Returns true if the path is not slef-intersecting
    and doesn't come across the inner hole
    """
    ...
  
  
  def fitness(self) -> np.float16:
    ...


class Population:
  def __init__(self):
    self.population = [Gene() for _ in range(Config.GeneticAlgoTuning.populationSize)]
    self.generationNumber = 0

  def nextGeneration(self) -> List[Gene]:
    for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
      self.fight()
      self.crossover()
      self.mutate()
      yield self.population
    
    raise StopIteration(f"Reached {Config.GeneticAlgoTuning.iterationsNumber} iterations")
  
  def fight(self):
    """This step filters out non-valid individuals and
    keeps only some of them according to the turnover rate
    """
    self.population = filter(
      lambda x: x.isValid(),
      self.population
    )

    newGenerationSize = Config.GeneticAlgoTuning.turnoverRate * Config.GeneticAlgoTuning.populationSize
    self.population = sorted(self.population)[ : int(newGenerationSize)]
  
  def crossover(self):
    jointsNumber = Config.GeneEncoding.segmentsNumber - 1
    cutpointIdx = randrange(jointsNumber)

  
  def mutate(self):
    ...


def main():
  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)
    
  pop = Population()
  for generation in pop.nextGeneration():
    print(generation) 


if __name__ == "__main__":
  main()
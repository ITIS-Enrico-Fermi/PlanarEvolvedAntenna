import logging
import numpy as np
from math import ceil, floor
from random import randrange, sample, choice, choices
from typing import List, Tuple
from config import Config
from core.gene import Gene


class Population:
  def __init__(self, pop_size: int):
    self.population = [Gene() for _ in range(pop_size)]
    self.generationNumber = 0
    self.king = Gene()

  def extractParent(self) -> Gene:
    """
    Interface method for parent extraction. Can be replaced with one the extractParent* methods.
    """
    return self.extractParentFitness()

  def extractParentIndex(self) -> Gene:
    """
    Extracts a random parent from the population, with no regard to gene fitness.
    """

    return choice(self.population)
  
  def extractParentFitness(self) -> Gene:
    """
    Extracts a parent from the population. The likelihood of extraction is proportional to gene fitness.
    """

    fitness = [g.fitness() for g in self.population]  # Can be cached, thus optimized
    fitness = [f + 500 if f > float("-inf") else 0 for f in fitness] # Increment trick

    return choices(self.population, weights=fitness)[0]


  def selectParents(self) -> List[Tuple[Gene]]:
    """
    Returns a list of parents, as tuples of (mother, father) of
    half the dimension of the current population
    """

    pop_size = len(self.population)
    parents_num = pop_size // 2
    
    parents = [
      (self.extractParent(pop_size), self.extractParent(pop_size)) for _ in range(parents_num)
    ]


  def generations(self) -> List[Gene]:
    for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
      self.generateOffspring()
      self.mutate()
      self.fight()
      
      self.fitnessMean = np.mean([g.fitnessCached for g in self.population])
      self.fitnessStdDev = np.std([g.fitnessCached for g in self.population])
      logging.info(
        f"\nFitness:\n"
        f"\tMean: {self.fitnessMean:.4f}\n"
        f"\tSd: {self.fitnessStdDev:.4f}\n"
        f"Population size: {len(self.population)}"
      )

      self.king = \
        self.population[0] if self.population[0].fitnessCached > self.king.fitnessCached else self.king
      
      if self.fitnessStdDev <= np.finfo(np.float32).eps:
        return

      self.generationNumber += 1
      yield self.population, self.generationNumber
    
  
  def fight(self):
    """This step filters out non-valid individuals and
    keeps only some of them according to the turnover rate
    """
    oldGenerationSize = len(self.population)

    self.population = list(
      filter(
      lambda x: x.isValid(),
      self.population
    ))

    logging.warning(f"Killed {oldGenerationSize - len(self.population)} ({(oldGenerationSize - len(self.population)) / oldGenerationSize * 100:.1f}%) genes")

    survivedGenesNumber = ceil(Config.GeneticAlgoTuning.turnoverRate * Config.GeneticAlgoTuning.populationSize)
    self.population = sorted(self.population, reverse=True)[ : survivedGenesNumber]
  
  def crossover(self, mother: Gene, father: Gene):
    cutpointIdx = randrange(Config.GeneEncoding.segmentsNumber)
    newGene1 = Gene(
      mother[:cutpointIdx] + father[cutpointIdx:],
      np.average([father.groundPlaneDistance, mother.groundPlaneDistance])
    )
    newGene2 = Gene(
      father[:cutpointIdx] + mother[cutpointIdx:],
      np.average([father.groundPlaneDistance, mother.groundPlaneDistance])
    )

    return newGene1, newGene2

  def generateOffspring(self):
    newGenerationSize = floor((1.0 - Config.GeneticAlgoTuning.turnoverRate) * Config.GeneticAlgoTuning.populationSize)
    oldGenerationSize = len(self.population)

    for _ in range(newGenerationSize // 2):
      momGene = self.extractParent()
      dadGene = self.extractParent()
      
      newGene1, newGene2 = self.crossover(momGene, dadGene)

      self.population.append(newGene1)
      self.population.append(newGene2)
    
  def mutate(self):
    toMutateSize = ceil(Config.GeneticAlgoTuning.mutationRate * len(self.population))
    genesToMutate = sample(self.population, k = toMutateSize)

    for gene in genesToMutate:
      mutationAngles = (np.random.rand(Config.GeneEncoding.segmentsNumber) - 0.5) \
        * Config.GeneEncoding.maxAngle

      mutationLengths = np.random.uniform(
        low = - (Config.GeneEncoding.minSegmentLen + Config.GeneEncoding.maxSegmentLen) / 2,
        high = (Config.GeneEncoding.minSegmentLen + Config.GeneEncoding.maxSegmentLen) / 2,
        size = Config.GeneEncoding.segmentsNumber
      )

      mutationGpDistance = np.random.uniform(
        low = Config.ShapeConstraints.groundPlaneDistanceMin,
        high = Config.ShapeConstraints.groundPlaneDistanceMax,
        size = 1
      )[0]

      newAngles = np.clip(
        gene.getAngleArray() + mutationAngles,
        - Config.GeneEncoding.maxAngle / 2,
        + Config.GeneEncoding.maxAngle / 2
      )

      newLengths = np.clip(
        gene.getLengthArray() + mutationLengths,
        Config.GeneEncoding.minSegmentLen,
        Config.GeneEncoding.maxSegmentLen
      )

      gene.setEncoding(newAngles, newLengths)
      gene.setGroundPlaneDistance(mutationGpDistance)
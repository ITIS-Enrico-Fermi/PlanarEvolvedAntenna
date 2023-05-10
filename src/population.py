import numpy as np
from math import ceil, floor
from random import randrange, sample
from typing import List
from config import Config
from gene import Gene


class Population:
  def __init__(self):
    self.population = [Gene() for _ in range(Config.GeneticAlgoTuning.populationSize)]
    self.generationNumber = 0

  def nextGeneration(self) -> List[Gene]:
    for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
      self.fight()
      self.crossover()
      self.mutate()
      self.generationNumber += 1
      yield self.population, self.generationNumber
    
  
  def fight(self):
    """This step filters out non-valid individuals and
    keeps only some of them according to the turnover rate
    """
    self.population = filter(
      lambda x: x.isValid(),
      self.population
    )

    survivedGenesNumber = ceil(Config.GeneticAlgoTuning.turnoverRate * Config.GeneticAlgoTuning.populationSize)
    self.population = sorted(self.population)[ : survivedGenesNumber]
  
  def crossover(self):
    newGenerationSize = floor((1.0 - Config.GeneticAlgoTuning.turnoverRate) * Config.GeneticAlgoTuning.populationSize)
    oldGenerationSize = len(self.population)

    for _ in range(newGenerationSize):
      cutpointIdx = randrange(Config.GeneEncoding.segmentsNumber)
      momGeneIdx = randrange(oldGenerationSize)
      dadGeneIdx = randrange(oldGenerationSize)
      momGene = self.population[momGeneIdx]
      dadGene = self.population[dadGeneIdx]
      newGene = Gene(momGene[:cutpointIdx] + dadGene[cutpointIdx:])
      self.population.append(newGene)
    
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
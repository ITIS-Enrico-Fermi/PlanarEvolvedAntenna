import logging
import numpy as np
from typing import List
from core.population import Population
from core.gene import Gene, NewGene
from random import choice, choices, randrange, random
from core.config import Config
from operator import itemgetter
from math import sqrt, floor, ceil

class NichePopulation(Population):
    def __init__(self, *args, **kwargs):
        self.worldHeight = Config.GeneticAlgoTuning.worldHeight
        self.worldWidth = Config.GeneticAlgoTuning.worldWidth

        super().__init__(
            self.worldHeight * self.worldWidth,
            Gene,
            *args, **kwargs
        )
        
        self.__post_init__()
        

    def __post_init__(self):
        self.world: np.ndarray = np.array(self.individuals).reshape(
            self.worldHeight,
            self.worldWidth
        )

        self.mutationRate = Config.GeneticAlgoTuning.mutationRate

    def fromPopulation(self, population: Population):
        self.individuals = population.individuals.copy()
        self.worldHeight = floor(sqrt(len(self.individuals)))
        self.worldWidth = floor(sqrt(len(self.individuals)))
        self.individuals = self.individuals[:(self.worldWidth*self.worldHeight)]
        self.generationNumber = population.generationNumber
        self.newbornsCounter = population.newbornsCounter
        self.killedGenes = population.killedGenes
        self.king = population.king

        self.__post_init__()

        return self

    def populationSet(self) -> np.ndarray:
        # TODO: unify this property with superclass population attribute
        return self.world.reshape(self.world.size)
    
    def nicheToSet(self, niche: np.ndarray) -> np.ndarray:
        return niche.reshape(niche.size)

    def extractParents(self, neigh: np.matrix) -> List[Gene]:
        """
        Extract parents for crossover from a neighbourhood (submatrix of world).
        """

        neigh = neigh.reshape(neigh.size)

        fitness = [g.fitness() for g in neigh]
        fitness = [500 + f if f > float("-inf") else 0 for f in fitness]

        try:
            return choices(neigh, weights=fitness, k=2)
        except ValueError:
            logging.warn("The niche has no fitting genes. Extracting without weights")
            return choices(neigh, k=2)


    def sampleNiche(self) -> np.ndarray:
        rows, cols = self.world.shape

        x = randrange(rows)
        y = randrange(cols)
        
        sliceX = np.array(range(x-3, x+4)) % self.worldHeight
        sliceY = np.array(range(y-3, y+4)) % self.worldWidth

        return self.world[sliceX, :][:, sliceY]

    def generateOffspring(self, niche: np.ndarray):
        for _ in range(ceil(Config.GeneticAlgoTuning.turnoverRate*niche.size)):
            mother, father = self.extractParents(niche)
            childA, childB = self.crossover(mother, father)

            self.newbornsCounter += 1
            
            if not childA.isValid() and not childB.isValid():
                continue
            
            if childA.isValid():
                child = childA
            if childB.isValid():
                child = childB
            if childA.isValid() and childB.isValid():
                child = childA if childA.fitness() > childB.fitness() else childB
            

            (x, y), weakest = min(np.ndenumerate(niche), key=itemgetter(1))
            if child > weakest:
                niche[x][y] = child

    def mutate(self, niche):
        for gene in self.nicheToSet(niche):
            if random() > Config.GeneticAlgoTuning.mutationRate:
                continue    # Because of uniform probability

            mutationAngles = np.random.uniform(
                -Config.GeneEncoding.maxAngle/Config.GeneEncoding.segmentsNumber,
                +Config.GeneEncoding.maxAngle/Config.GeneEncoding.segmentsNumber,
                Config.GeneEncoding.segmentsNumber
            )

            mutationLengths = np.random.uniform(
                low = - (Config.GeneEncoding.maxSegmentLen - Config.GeneEncoding.minSegmentLen) / 2,
                high = (Config.GeneEncoding.maxSegmentLen - Config.GeneEncoding.minSegmentLen) / 2,
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
            gene.setGroundPlaneDistance((mutationGpDistance + gene.groundPlaneDistance) / 2)            

    def cleanup(self, niche: np.ndarray):
        """
        This step filters out non-valid individuals
        """
        self.killedGenes = 0

        for (i, j), gene in np.ndenumerate(niche):
            if not gene.isValid():
                self.killedGenes += 1
                niche[i][j] = Gene()

        self.killedGenesRatio = self.killedGenes / niche.size
                

    def generations(self) -> List[Gene]:
        for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
            niche = self.sampleNiche()
            self.generateOffspring(niche)
            self.mutate(niche)
            self.cleanup(niche)

            validPop = list(
                filter(
                    lambda x: x.isValid(),
                    self.populationSet().tolist()
                )
            )

            self.fitnessMean = np.mean([g.fitness() for g in validPop])
            self.fitnessStdDev = np.std([g.fitness() for g in validPop])
            logging.info(
                f"\nFitness:\n"
                f"\tMean: {self.fitnessMean:.4f}\n"
                f"\tSd: {self.fitnessStdDev:.4f}\n"
                f"Population size: {self.world.size}"
            )

            self.king = max(self.populationSet())

            # if self.fitnessStdDev <= np.finfo(np.float32).eps:
            #     return

            self.generationNumber += 1
            yield sorted(validPop, reverse=True), self.generationNumber


if __name__ == '__main__':
    p = NichePopulation()
    p.generateOffspring()
from typing import List
from core.population import Population
from core.gene import Gene
from config import Config
from random import choices
import numpy as np
from operator import itemgetter
from random import randrange
import logging

class NichePopulation(Population):
    def __init__(self, mutationRate: float):
        super().__init__(Config.GeneticAlgoTuning.worldHeight * Config.GeneticAlgoTuning.worldWidth)
        
        self.world: np.ndarray = np.array(self.population).reshape(
            Config.GeneticAlgoTuning.worldHeight,
            Config.GeneticAlgoTuning.worldWidth
        )

        self.mutationRate = mutationRate

    def populationSet(self) -> np.ndarray:
        # TODO: unify this property with superclass population attribute
        return self.world.reshape(self.world.size)

    def extractParents(self, neigh: np.matrix):
        """
        Extract parents for crossover from a neighbourhood (submatrix of world).
        """

        neigh = neigh.reshape(neigh.size)

        fitness = [g.fitness() for g in neigh]
        fitness = [100 + f if f > float("-inf") else 0 for f in fitness]

        return choices(neigh, weights=fitness, k=2)
    
    def generateOffspring(self):
        rows, cols = self.world.shape
        
        x = randrange(rows)
        y = randrange(cols)

        neigh = self.world[x-1:x+2, y-1:y+2]

        mother, father = self.extractParents(neigh)
        childA, childB = self.crossover(mother, father)

        self.mutate(childA)

        if not childA.isValid():
            return

        (x, y), weakest = min(np.ndenumerate(neigh), key=itemgetter(1))
        if childA > weakest:
            neigh[x][y] = childA
            print(f"Sub ({x}, {y}) with child A with fitness: {childA}")
        
    def mutate(self, gene: Gene):
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
            

    def fight():
        pass

    def generations(self) -> List[Gene]:
        for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
            self.generateOffspring()

            self.fitnessMean = np.mean([g.fitness() for g in self.populationSet()])
            self.fitnessStdDev = np.std([g.fitness() for g in self.populationSet()])
            logging.info(
                f"\nFitness:\n"
                f"\tMean: {self.fitnessMean:.4f}\n"
                f"\tSd: {self.fitnessStdDev:.4f}\n"
                f"Population size: {self.world.size}"
            )

            self.king = max(self.populationSet())

            if self.fitnessStdDev <= np.finfo(np.float32).eps:
                return

            self.generationNumber += 1
            yield sorted(self.populationSet().tolist(), reverse=True), self.generationNumber


if __name__ == '__main__':
    p = NichePopulation(0.05)
    p.generateOffspring()
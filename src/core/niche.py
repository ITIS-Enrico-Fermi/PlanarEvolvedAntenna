from typing import List
from core.population import Population
from core.gene import Gene
from config import Config
from random import choices, randrange, random
import numpy as np
from operator import itemgetter
import logging
from utils.geometry import polychainToCartesian, cartesianToPolychain

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
    
    def nicheToSet(self, niche: np.ndarray) -> np.ndarray:
        return niche.reshape(niche.size)

    def extractParents(self, neigh: np.matrix):
        """
        Extract parents for crossover from a neighbourhood (submatrix of world).
        """

        neigh = neigh.reshape(neigh.size)

        fitness = [g.fitness() for g in neigh]
        fitness = [10000 + f if f > float("-inf") else 0 for f in fitness]

        print("Fitness: ", fitness)

        return choices(neigh, weights=fitness, k=2)
    
    def sampleNiche(self) -> np.ndarray:
        rows, cols = self.world.shape

        x = randrange(rows)
        y = randrange(cols)

        return self.world.take(
            [range(x-1, x+2),
            range(y-1, y+2)],
            mode='wrap'                       
        )

    def generateOffspring(self, niche: np.ndarray):
        mother, father = self.extractParents(niche)
        childA, childB = self.crossover(mother, father)

        if not childA.isValid():
            return

        (x, y), weakest = min(np.ndenumerate(niche), key=itemgetter(1))
        if childA > weakest:
            niche[x][y] = childA
            print(f"Sub ({x}, {y}) with child A with fitness: {childA}")
        
    def mutate(self, niche):
        for gene in self.nicheToSet(niche):
            if random() > Config.GeneticAlgoTuning.mutationRate:
                continue    # Because of uniform probability

            mutationGpDistance = np.random.uniform(
                low = Config.ShapeConstraints.groundPlaneDistanceMin,
                high = Config.ShapeConstraints.groundPlaneDistanceMax,
                size = 1
            )[0]

            """
            xMutation = np.random.uniform(
                low = -0.2,
                high = 0.2,
                size = Config.GeneEncoding.segmentsNumber + 1
            )
            """
            xMutation = np.array([0] * (Config.GeneEncoding.segmentsNumber + 1))

            yMutation = np.random.uniform(
                low = - (Config.GeneEncoding.minSegmentLen + Config.GeneEncoding.maxSegmentLen) / 2,
                high = (Config.GeneEncoding.minSegmentLen + Config.GeneEncoding.maxSegmentLen) / 2,
                size = Config.GeneEncoding.segmentsNumber + 1
            )

            newEncoding = gene.encoding
            newEncoding += np.column_stack((xMutation, yMutation))

            gene.setEncoding(newEncoding)
            gene.setGroundPlaneDistance(mutationGpDistance)
            

    def fight():
        pass

    def generations(self) -> List[Gene]:
        for _ in range(Config.GeneticAlgoTuning.iterationsNumber):
            niche = self.sampleNiche()
            self.generateOffspring(niche)
            self.mutate(niche)

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
from core.population import Population
from core.gene import Gene
from config import Config
from random import choices
import numpy as np

class NichePopulation(Population):
    def __init__(self):
        super().__init__(Config.GeneticAlgoTuning.worldHeight * Config.GeneticAlgoTuning.worldWidth)
        
        self.world: np.ndarray = np.array(self.population).reshape(
            Config.GeneticAlgoTuning.worldHeight,
            Config.GeneticAlgoTuning.worldWidth
        )

    def extractParents(self, kernel_i: int, kernel_j: int, kernel_dim: int):
        """
        Extract parents for crossover from a kernel (submatrix of world).
        """

        submatrix = self.world[kernel_i:kernel_i+kernel_dim, kernel_j:kernel_j+kernel_dim]
        submatrix = submatrix.tolist()

        fitness = [g.fitness() for g in submatrix]
        fitness = [500 + f if f > float("-inf") else 0 for f in fitness]

        return choices(submatrix, weights=fitness, k=2)
    
    def generateOffspring(self):
        rows, cols = self.world.shape
        kernel_dim = 3

        for i in range(rows - kernel_dim):
            for j in range(cols - kernel_dim):
                mother, father = self.extractParentKernel(i, j)
                childA, childB = self.crossover(mother, father)

                # substitute neighbours with a lower fitness with children

    def mutate():
        pass

    def fight():
        pass
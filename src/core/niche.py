from core.population import Population
from core.gene import Gene
from config import Config
from random import choices
import numpy as np
from operator import itemgetter
from random import randrange

class NichePopulation(Population):
    def __init__(self):
        super().__init__(Config.GeneticAlgoTuning.worldHeight * Config.GeneticAlgoTuning.worldWidth)
        
        self.world: np.ndarray = np.array(self.population).reshape(
            Config.GeneticAlgoTuning.worldHeight,
            Config.GeneticAlgoTuning.worldWidth
        )

    def extractParents(self, kernel: np.matrix):
        """
        Extract parents for crossover from a kernel (submatrix of world).
        """

        submatrix = kernel.tolist()

        fitness = [g.fitness() for g in submatrix]
        fitness = [500 + f if f > float("-inf") else 0 for f in fitness]

        return choices(submatrix, weights=fitness, k=2)
    
    def generateOffspring(self):
        rows, cols = self.world.shape
        
        x, y = randrange(...)

        submatrix = self.world[i:i+kernel_dim, j:j+kernel_dim]

        mother, father = self.extractParents(submatrix)
        childA, childB = self.crossover(mother, father)

        for x, y, competitor in sorted(np.ndenumerate(submatrix), key=itemgetter(2)):
            if(childA > competitor):
                submatrix[x][y] = childA
                break
        
        for x, y, competitor in sorted(np.ndenumerate(submatrix), key=itemgetter(2)):
            if(childB > competitor):
                submatrix[x][y] = childB

    def mutate():
        pass

    def fight():
        pass


if __name__ == '__main__':
    p = NichePopulation()
    p.generateOffspring()
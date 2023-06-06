import logging
import numpy as np
from necpp import *
from config import Config
from utils.geometry import *
from rf.radiation import RadiationPattern, RpCardEvaluationInput
from rf.nec_analysis import NecAnalysis
import matplotlib.pyplot as plt

class Gene:
    globalSerial = 0
    GAIN_K = 1
    STANDARD_DEVIATION_K = 0
    # STANDARD_DEVIATION_K = -1    # Penalize high sd

    def __init__(self, providedGenotype = None, gndDistance: float = 1.0):
        self.FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)

        self.radiationPatternSagittal = None
        self.radiationPatternFrontal = None
        self.fitnessCached = float("-inf")
        self.groundPlaneDistance = np.random.uniform(
            low = Config.ShapeConstraints.groundPlaneDistanceMin,
            high = Config.ShapeConstraints.groundPlaneDistanceMax,
            size = 1
        )[0]

        self.serial = Gene.globalSerial
        Gene.globalSerial += 1

        if not providedGenotype is None:
            self.encoding = providedGenotype
            self.groundPlaneDistance = gndDistance

        else:
            points = randomPointsInsideCircle(Config.GeneEncoding.segmentsNumber + 1, Config.ShapeConstraints.outerDiam/2)
            self.encoding = points


    def __lt__(self, other) -> bool:
        return self.fitness() < other.fitness()
    
    def __repr__(self) -> str:
        return f"<Gene {self.serial} {repr(self.encoding)}>"
    
    def __getitem__(self, itemIdx):
        return self.encoding[itemIdx]

    def getCartesianCoords(self) -> List[Segment]:
        return self.encoding

    def getRadiationPatternSagittal(self) -> RadiationPattern:
        return self.radiationPatternSagittal
    
    def getRadiationPatternFrontal(self) -> RadiationPattern:
        return self.radiationPatternFrontal
    
    def setEncoding(self, chain: Polychain):
        self.encoding = chain

        # Invalidate cached fitness
        self.fitnessCached = float("-inf")

    def getPolychain(self) -> Polychain:
        """
        Returns a polychain (list of segments) to use in NEC analysis
        """

        return cartesianToPolychain(self.encoding)
    
    def setGroundPlaneDistance(self, gpDist: float) -> None:
        self.groundPlaneDistance = gpDist

    def isValid(self) -> bool:
        """
        Returns true if the path is not self-intersecting
        and doesn't come across the inner hole
        """
        OUTER_RADIUS = Config.ShapeConstraints.outerDiam / 2
        INNER_RADIUS = Config.ShapeConstraints.innerDiam / 2
        
        return (
            not isSelfIntersectingPath(self.getPolychain()) and
            not doesPathIntersectCircle(self.getPolychain(), Point(Config.ShapeConstraints.centerShift, 0), INNER_RADIUS) and
            isPathInCircle(self.getPolychain(), Point(0, 0), OUTER_RADIUS)
        )

    def fitness(self) -> np.float16:
        freqHz = Config.ShapeConstraints.targetFreq

        if self.fitnessCached > float("-inf"):
            return self.fitnessCached

        try:
            with NecAnalysis(self, freqHz) as sim:
                context = sim.getNecContext()

                sim.addInfiniteGroundPlane()
                sim.runExcitation()
                
                self.radiationPatternSagittal = sim.computeRadiationPattern([
                    RpCardEvaluationInput(60, 0, -15, 45, 45, 0, 0),    # sagittal plane (1)
                    RpCardEvaluationInput(15, 60, 15, 225, 225, 0, 1)    # sagittal plane (2)
                ])

                self.radiationPatternFrontal = sim.computeRadiationPattern([
                    RpCardEvaluationInput(60, 0, -15, 135, 135, 0, 2),    # frontal plane (1)
                    RpCardEvaluationInput(15, 60, 15, 315, 315, 0, 3)    # frontal plane (2)
                ])


                min_gain = min([nec_gain_min(context, i) for i in range(4)])
                sd_gain = max([nec_gain_sd(context, i) for i in range(4)])
                max_gain = max([nec_gain_max(context, i) for i in range(4)])
                self.fitnessCached = self.GAIN_K * min_gain + self.STANDARD_DEVIATION_K * sd_gain
                
                logging.debug(
                    f"Gain\n"
                    f"\tmin: {min_gain}\n"
                    f"\tmax: {max_gain}\n"
                    f"\tsd: {sd_gain}\n"
                    # f"\tmean: {nec_gain_mean(context, 0)}\n"
                )

        except AssertionError:
            print(nec_error_message())
            self.fitnessCached = float("-inf")    # This gene will be discarded at the next iteration

        return self.fitnessCached

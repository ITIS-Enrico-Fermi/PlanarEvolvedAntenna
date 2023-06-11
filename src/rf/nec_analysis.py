from necpp import *
from typing import List, Any
from rf.radiation import RadiationPattern, RpCardEvaluationInput

class NecAnalysis:
    def __init__(self, gene, frequencyHz: float):
        self.context = None
        self.gene = gene
        self.frequencyHz = frequencyHz
    
    def __enter__(self):
        self.context = nec_create()
        
        for segment in self.gene.getPolychain():
            assert nec_wire(
                self.context,
                self.gene.globalSerial,    # tag ID
                1,    # Segment count
                segment.start.x / 1000,    # Start point x in m
                segment.start.y / 1000,    # Start point y in m
                self.gene.groundPlaneDistance / 1000,    # Start point z in m
                segment.end.x / 1000,    # Start point x in m
                segment.end.y / 1000,    # Start point y in m
                self.gene.groundPlaneDistance / 1000, # Start point z in m
                0.0001,    # First segment radius
                1,    # Uniform length
                1    # Ratio of adjacent segments
            ) == 0
        
        assert nec_geometry_complete(self.context, 0) == 0    # inner 0 means no ground-plane
        return self

    def __exit__(self, *_):
        nec_delete(self.context)
    
    def getNecContext(self) -> Any:
        return self.context

    def addInfiniteGroundPlane(self) -> None:
        assert nec_gn_card(self.context, 1, 0, 0, 0, 0, 0, 0, 0) == 0
    
    def runExcitation(self) -> None:
        assert nec_fr_card(    # Frequency
            self.context,
            0,    # Linear range
            1,    # One frequency
            self.frequencyHz / 1e6,    # Frequency in MHz
            0    # Frequency step
        ) == 0

        assert nec_ex_card(    # Excitation
            self.context,
            0,    # Voltage source excitation
            self.gene.globalSerial,    # Tag number (from source segment)
            1,    # N-th segment of the source set of segments
            0,
            1.0, 0, 0, 0, 0, 0    # Tmp
        ) == 0
    
    def computeRadiationPattern(self, evaluations: List[RpCardEvaluationInput]) -> RadiationPattern:
        for eval in evaluations:
            assert nec_rp_card(    # Radiation Pattern
                self.context,
                0,    # Normal calc mode
                eval.thetaNum,    # Number of theta angles
                eval.phiNum,    # Number of phi angles
                0,    # Major-minor axes
                5,    # Total gain normalized
                0,    # Power gain
                0,    # Do averaging
                eval.thetaStart,    # Theta zero
                eval.phiStart,    # Phi zero
                eval.thetaIncrement,    # Theta increment in deg
                eval.phiIncrement,    # Phi increment in deg
                0,    # Radial distance from origin
                0,    # Normalization factor
            ) == 0

        return RadiationPattern.fromNecContext(
            self.context,
            [
                RpCardEvaluationInput(
                    90 - evaluations[0].thetaStart,
                    90 - evaluations[0].thetaEnd,
                    evaluations[0].thetaIncrement,
                    evaluations[0].phiStart,
                    evaluations[0].phiEnd,
                    evaluations[0].phiIncrement,
                    evaluations[0].index
                ),
                RpCardEvaluationInput(
                    90 + evaluations[1].thetaStart,
                    90 + evaluations[1].thetaEnd,
                    evaluations[1].thetaIncrement,
                    evaluations[1].phiStart,
                    evaluations[1].phiEnd,
                    evaluations[1].phiIncrement,
                    evaluations[1].index
                )
            ]
        )
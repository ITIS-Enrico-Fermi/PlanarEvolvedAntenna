from dataclasses import dataclass
from typing import List
from necpp import *

@dataclass
class RadiationPattern():
    """Class to represent a radiation pattern. Computation output of NEC"""
    gains_db: List[float]
    thetas: List[float]
    phis: List[float]

    @classmethod
    def from_nec_context(self, ctx):
        gains_db = [nec_gain(ctx, 0, i, 0) for i in range(0, 12)]
        #self.gains = list(map(lambda g: 10.0**(g / 10.0), self.gains_db))
        thetas = [i * 15 * 3.1415 / 180.0 for i in range(0, 12)]
        phis = [0]*12

        return RadiationPattern(gains_db, thetas, phis)
    
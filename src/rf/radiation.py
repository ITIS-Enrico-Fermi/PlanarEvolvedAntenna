import numpy as np
from necpp import *
from typing import List
from dataclasses import dataclass, field

@dataclass
class RpCardEvaluationInput:
  thetaStart: float = field(default_factory=float)
  thetaEnd: float = field(default_factory=float)
  thetaIncrement: float = field(default_factory=float)
  thetaNum: float = field(default_factory=float, init=False)

  phiStart: float = field(default_factory=float)
  phiEnd: float = field(default_factory=float)
  phiIncrement: float = field(default_factory=float)
  phiNum: float = field(default_factory=float, init=False)
  
  index: int = field(default_factory=int)

  def __post_init__(self):
    self.thetaNum = abs(self.thetaEnd - self.thetaStart) // abs(self.thetaIncrement) + 1 if self.thetaIncrement != 0 else 1
    self.phiNum = abs(self.phiEnd - self.phiStart) // abs(self.phiIncrement) + 1 if self.phiIncrement != 0 else 1

@dataclass
class RadiationPattern:
  """Class to represent a radiation pattern. Computation output of NEC"""
  gainsMw: List[float] = field(default_factory=list)
  thetasRad: List[float] = field(default_factory=list)
  phisRad: List[float] = field(default_factory=list)
  groundPlaneDistance: float = field(default_factory=float)

  @classmethod
  def fromNecContext(cls, ctx, rpEvaluations: List[RpCardEvaluationInput]):
    gainsMw = []
    thetasRad = []
    phisRad = []

    for evaluation in rpEvaluations:
      assert evaluation.thetaEnd >= evaluation.thetaStart
      assert evaluation.phiEnd >= evaluation.phiStart
      gainsDb = np.array([
        nec_gain(ctx, evaluation.index, i, j)
        for i in range(evaluation.thetaNum)
        for j in range(evaluation.phiNum)
      ])

      thetasDeg = np.linspace(evaluation.thetaStart, evaluation.thetaEnd, evaluation.thetaNum)      
      phisDeg = np.linspace(evaluation.phiStart, evaluation.phiEnd, evaluation.phiNum)
      
      gainsMw += list(10 ** (gainsDb / 10))
      thetasRad += list(thetasDeg * np.pi / 180)
      phisRad += list(phisDeg * np.pi / 180)

    return RadiationPattern(gainsMw, thetasRad, phisRad)
    
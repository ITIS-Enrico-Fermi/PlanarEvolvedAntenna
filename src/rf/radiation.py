import numpy as np
from necpp import *
from typing import List
from dataclasses import dataclass, field

@dataclass(frozen=True)
class RpCardEvaluationInput:
  thetaStart: float = field(default_factory=float)
  thetaEnd: float = field(default_factory=float)
  thetaIncrement: float = field(default_factory=float)
  phiStart: float = field(default_factory=float)
  phiEnd: float = field(default_factory=float)
  phiIncrement: float = field(default_factory=float)

@dataclass
class RadiationPattern:
  """Class to represent a radiation pattern. Computation output of NEC"""
  gainsMw: List[float] = field(default_factory=list)
  thetasRad: List[float] = field(default_factory=list)
  phisRad: List[float] = field(default_factory=list)

  @classmethod
  def fromNecContext(cls, ctx, rpEvaluations: List[RpCardEvaluationInput]):
    gainsMw = []
    thetasRad = []
    phisRad = []

    for evalIdx, evaluation in enumerate(rpEvaluations):
      assert evaluation.thetaEnd >= evaluation.thetaStart
      assert evaluation.phiEnd >= evaluation.phiStart
      thetaNum = (evaluation.thetaEnd - evaluation.thetaStart) // abs(evaluation.thetaIncrement) + 1
      phiNum = (evaluation.phiEnd - evaluation.phiStart) // abs(evaluation.phiIncrement) + 1
      gainsDb = np.array([
        nec_gain(ctx, evalIdx, i, j)
        for i in range(abs(thetaNum))
        for j in range(abs(phiNum))
      ])

      thetasDeg = \
        np.linspace(evaluation.thetaStart, evaluation.thetaEnd, thetaNum) if evaluation.thetaIncrement > 0 \
        else np.linspace(evaluation.thetaEnd, evaluation.thetaStart, thetaNum)
      
      phisDeg = \
        np.linspace(evaluation.phiStart, evaluation.phiEnd, phiNum) if evaluation.phiIncrement > 0 \
        else np.linspace(evaluation.phiEnd, evaluation.phiStart, phiNum)
      
      gainsMw += list(10 ** (gainsDb / 10))
      thetasRad += list(thetasDeg * np.pi / 180)
      phisRad += list(phisDeg * np.pi / 180)

    return RadiationPattern(gainsMw, thetasRad, phisRad)
    
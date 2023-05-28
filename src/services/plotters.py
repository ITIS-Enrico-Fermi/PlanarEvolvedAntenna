from typing import Any
from abc import ABC, abstractmethod
from core.population import Population
from matplotlib.figure import Figure
from services.service import Service

class IPlotterService(Service):
  def __init__(self, figure: Figure):
    self.figure = figure

  @abstractmethod
  def plot(self, population: Population) -> Any:
    ...

class StubPlotterService(IPlotterService):
  def plot(self, population: Population) -> None:
    return

class PlanarShapePlotter(IPlotterService):
  """
  2D geometry and constraints plotter
  """
  def plot(self, population: Population) -> None:
    ...

class RadiationPatternPlotter(IPlotterService):
  """
  Frontal and sagittal radiation pattern plotter
  """
  def plot(self, population: Population) -> None:
    ...

class FitnessPlotter(IPlotterService):
  """
  Fitness max, mean and standard deviation plotter
  """
  def plot(self, population: Population) -> None:
    ...

class HammingDistancePlotter(IPlotterService):
  """
  Mean hamming distance between population's genes plotter
  """
  def plot(self, population: Population) -> None:
    ...


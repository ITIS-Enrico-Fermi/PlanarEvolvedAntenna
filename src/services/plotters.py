from typing import Any, Callable
from abc import ABC, abstractmethod
from core.population import Population
from services.service import Service
from matplotlib.axes import Axes
from utils.amenities import *

class IPlotterService(Service):
  def __init__(self, axes: Axes):
    self.axes = axes

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
    self.axes.axis("equal")
    self.axes.clear()
    plotCansatBottomProfile(self.axes)
    plotAntennaPath(self.axes, population.individuals[0].getCartesianCoords())


class RadiationPatternPlotter(IPlotterService):
  """
  Frontal and sagittal radiation pattern plotter
  """
  def __init__(self, axes: Axes, rpGetter: Callable[[], RadiationPattern]):
    self.axes = axes
    self.rpGetter = rpGetter
  
  def plot(self, population: Population) -> None:
    self.axes.clear()
    
    plotCansatProfile(
      self.axes,
      max(self.rpGetter(population.individuals[0]).gainsMw),
      -population.individuals[0].groundPlaneDistance/30
    )

    plotRadiationPatternSlice(
        self.axes,
        self.rpGetter(population.individuals[0])
    )


class FitnessPlotter(IPlotterService):
  """
  Fitness max, mean and standard deviation plotter
  """
  def __init__(self, axes: Axes):
    self.axes = axes
    self.meanValues = []
    self.sdValues = []

  def plot(self, population: Population) -> None:
    self.meanValues.append(population.fitnessMean)
    self.sdValues.append(population.fitnessStdDev)
    time = list(range(population.generationNumber))

    self.axes.clear()
    self.axes.set_title("Fitness")
    self.axes.grid(True)
    self.axes.plot(
      time, self.meanValues,
      time, self.sdValues
    )

class HammingDistancePlotter(IPlotterService):
  """
  Mean hamming distance between population's genes plotter
  """
  def plot(self, population: Population) -> None:
    ...

class KilledGenesPlotter(IPlotterService):
  """
  Number of killed  genes plotter
  """
  def __init__(self, axes: Axes):
    self.axes = axes
    self.killedGenes = []

  def plot(self, population: Population) -> None:
    self.killedGenes.append(population.killedGenesRatio)
    time = list(range(population.generationNumber))

    self.axes.clear()
    self.axes.set_title("Killed genes ratio")
    self.axes.grid(True)
    self.axes.plot(
      time, self.killedGenes,
    )

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
    self.maxValues = []
    self.sdValues = []
    self.timeline = []

  def plot(self, population: Population) -> None:
    self.timeline.append(population.newbornsCounter)
    self.meanValues.append(population.fitnessMean)
    self.maxValues.append(population.king.fitness())
    self.sdValues.append(population.fitnessStdDev)

    self.axes.clear()
    self.axes.set_title("Fitness")
    self.axes.grid(True)
    self.axes.plot(
      self.timeline, self.meanValues,
      self.timeline, self.maxValues,
      self.timeline, self.sdValues
    )

class EuclideanDistancePlotter(IPlotterService):
  """
  Mean hamming distance between population's genes plotter
  """
  def __init__(self, axes: Axes):
    self.axes = axes
    self.timeline = []
    self.euclideanDistance = []
  
  def plot(self, population: Population) -> None:
    self.timeline.append(population.newbornsCounter)
    kingX = np.array(list(map(lambda seg: seg.start.x, population.king.polychainEncoding)))
    kingY = np.array(list(map(lambda seg: seg.start.y, population.king.polychainEncoding)))

    for individual in population.individuals:
      othersX = np.array(list(map(lambda seg: seg.start.x, individual.polychainEncoding)))
      othersY = np.array(list(map(lambda seg: seg.start.y, individual.polychainEncoding)))
    
    kingNodes = np.array(list(zip(kingX, kingY)))
    othersNodes = np.array(list(zip(othersX, othersY)))

    self.euclideanDistance.append(np.sum(np.linalg.norm(kingNodes - othersNodes, axis=1)) / len(population.individuals))

    self.axes.clear()
    self.axes.set_title("Distance from king")
    self.axes.grid(True)
    self.axes.plot(
      self.timeline, self.euclideanDistance,
    )

class KilledGenesPlotter(IPlotterService):
  """
  Number of killed  genes plotter
  """
  def __init__(self, axes: Axes):
    self.axes = axes
    self.killedGenes = []
    self.timeline = []

  def plot(self, population: Population) -> None:
    self.timeline.append(population.newbornsCounter)
    self.killedGenes.append(population.killedGenesRatio)

    self.axes.clear()
    self.axes.set_title("Killed genes ratio")
    self.axes.grid(True)
    self.axes.plot(
      self.timeline, self.killedGenes,
    )

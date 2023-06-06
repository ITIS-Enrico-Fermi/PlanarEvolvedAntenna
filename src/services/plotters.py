from typing import Dict, Any, Callable
from abc import ABC, abstractmethod
from core.population import Population
from services.service import Service
from matplotlib.axes import Axes
from utils.amenities import *

class IPlotterService(Service):
  def __init__(self, axes: Axes):
    self.axes = axes
    self.__post_init__()

  def __post_init__(self) -> Any:
    ...

  @abstractmethod
  def plot(self, population: Population) -> Any:
    ...


class IGrapherService(IPlotterService):
  def __init__(self, axes: Axes, plotNumber: int):
    self.axes = axes
    self.plotNum = plotNumber
    self.__post_init__()

  def __post_init__(self) -> Any:
    ...
  
  @abstractmethod
  def plot(self, population: Population) -> Dict[str, List]:
    """plots on axes and returns a dictionary of plotted values.
    @return what it has just plotted in a dictionary. Keys will be used as labels.
    """
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


class FitnessPlotter(IGrapherService):
  """
  Fitness max, mean and standard deviation plotter
  """
  def __post_init__(self):
    self.timeline = []
    self.meanValues = []
    self.maxValues = []
    self.sdValues = []

  def plot(self, population: Population) -> Dict[str, List]:
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
    self.axes.legend(["mean", "max", "sd"])

    return {
      f"timeline{self.plotNum}": self.timeline,
      f"meanFitness{self.plotNum}": self.meanValues,
      f"maxFitness{self.plotNum}": self.maxValues,
      f"sdFitness{self.plotNum}": self.sdValues
    }


class EuclideanDistancePlotter(IGrapherService):
  """
  Mean hamming distance between population's genes plotter
  """
  def __post_init__(self):
    self.timeline = []
    self.euclideanDistanceValues = []
  
  def plot(self, population: Population) -> Dict[str, List]:
    self.timeline.append(population.newbornsCounter)
    kingX = np.array(list(map(lambda seg: seg.start.x, population.king.polychainEncoding)))
    kingY = np.array(list(map(lambda seg: seg.start.y, population.king.polychainEncoding)))

    for individual in population.individuals:
      othersX = np.array(list(map(lambda seg: seg.start.x, individual.polychainEncoding)))
      othersY = np.array(list(map(lambda seg: seg.start.y, individual.polychainEncoding)))
    
    kingNodes = np.array(list(zip(kingX, kingY)))
    othersNodes = np.array(list(zip(othersX, othersY)))

    self.euclideanDistanceValues.append(
      np.sum(np.linalg.norm(kingNodes - othersNodes, axis=1)) / len(population.individuals)
    )

    self.axes.clear()
    self.axes.set_title("Distance from king")
    self.axes.grid(True)
    self.axes.plot(
      self.timeline, self.euclideanDistanceValues,
    )

    return {
      f"timeline{self.plotNum}": self.timeline,
      f"kingDistance{self.plotNum}": self.euclideanDistanceValues
    }


class KilledGenesPlotter(IGrapherService):
  """
  Number of killed  genes plotter
  """
  def __post_init__(self):
    self.timeline = []
    self.killedGenes = []

  def plot(self, population: Population) -> Dict[str, List]:
    self.timeline.append(population.newbornsCounter)
    self.killedGenes.append(population.killedGenesRatio)

    self.axes.clear()
    self.axes.set_title("Killed genes ratio")
    self.axes.grid(True)
    self.axes.plot(
      self.timeline, self.killedGenes,
    )

    return {
      f"timeline{self.plotNum}": self.timeline,
      f"killedGenes{self.plotNum}": self.killedGenes
    }

from abc import abstractclassmethod, abstractmethod
from typing import List, Any
from services.service import Service
from services.plotters import IGrapherService
from core.population import Population
from matplotlib.axes import Axes
from scipy.io import savemat

class AxesStub(Axes):
  def clear(self, *_):
    pass

  def grid(self, *_):
    pass
  
  def plot(self, *_):
    pass


class IStatService(Service):
  def __init__(self, filename: str):
    self.filename = filename
    self.graphers = []
  
  def withGraphers(self, *graphers: List[IGrapherService]) -> Any:
    self.graphers += graphers
    return self
  
  def withGrapher(self, grapher: IGrapherService) -> Any:
    self.graphers.append(grapher)
    return self

  @abstractmethod
  def stat(self, population: Population) -> None:
    ...


class StatService(IStatService):
  def stat(self, population: Population) -> None:
    mergedDict = {}
    
    for grapher in self.graphers:
      mergedDict |= grapher.plot(population)

    savemat(self.filename, mergedDict)
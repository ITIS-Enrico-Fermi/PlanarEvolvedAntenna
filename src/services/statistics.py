from abc import abstractclassmethod, abstractmethod
from sre_constants import ANY_ALL
from typing import List, Dict, Any
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

class ICollectorService(Service):
  def __init__(self, filename: str):
    self.filename = filename
    self.dataDict = {}
  
  def updateData(self, dataDict: Dict[str, List]) -> None:
    ...

class IStatService(Service):
  def __init__(self, filename: str):
    self.filename: str = filename
    self.graphers: List[IGrapherService] = []
    self.collectors: List[ICollectorService] = []
    self.valuesDict: Dict[str, List] = {}
  
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

    self.valuesDict = mergedDict
    savemat(self.filename, mergedDict)

class AggregateStatService(ICollectorService):
  def __init__(self, filename: str):
    self.filename: str = filename
  
  def updateData(self, dataDict: Dict[str, List]) -> None:
    ...
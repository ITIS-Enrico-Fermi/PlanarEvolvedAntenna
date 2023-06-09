from abc import abstractclassmethod, abstractmethod
from heapq import merge
from sre_constants import ANY_ALL
from typing import List, Dict, Any
from services.service import Service
from services.plotters import IGrapherService
from core.population import Population
from matplotlib.axes import Axes
from scipy.io import savemat
from collections import defaultdict

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
  def stat(self, population: Population) -> Dict[str, List]:
    ...


class StubStatService(IStatService):
  def stat(self, population: Population) -> Dict[str, List]:
    for grapher in self.graphers:
      grapher.plot(population)


class StatService(IStatService):
  def stat(self, population: Population) -> Dict[str, List]:
    mergedDict = {}
    
    for grapher in self.graphers:
      mergedDict |= grapher.plot(population)

    self.valuesDict = mergedDict
    savemat(self.filename, mergedDict)
    return mergedDict


class StubAggregator(ICollectorService):
  def __init__(self):
    pass

  def stat(self, *_):
    pass


class AggregateStatService(ICollectorService):
  def __init__(self, filename: str):
    self.filename: str = filename
    self.dataSnapshots: dict[int, List[Dict[str, List]]] = defaultdict(list)

  def updateData(self, dataDict: Dict[str, List]) -> None:
    self.dataSnapshots[dataDict['timeline'][-1]].append(dataDict.copy())
    print(self.dataSnapshots)

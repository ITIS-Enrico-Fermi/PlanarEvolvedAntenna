from fileinput import filename
from os.path import join
from typing import Any
from abc import ABC, abstractmethod
from core.population import Population
from services.service import Service
from utils.amenities import *

class IPersistenceService(Service):
  def __init__(self, persistenceFolder: str):
    self.persistenceFolder = persistenceFolder
    
  @abstractmethod
  def save(self, population: Population) -> Any:
    ...

class StubPersistenceService(IPersistenceService):
  def save(self, population: Population) -> None:
    pass


class MiniaturePersistenceService(IPersistenceService):
  def save(self, population: Population) -> None:
    fileName = f"gen{population.generationNumber}.svg"
    filePath = join(
      self.persistenceFolder,
      fileName
    )

    with open(filePath, "w") as outFile:
      saveMiniaturesSvg(outFile, population.individuals, False)


class MiniatureWithBoundariesPersistenceService(IPersistenceService):
  def save(self, population: Population) -> None:
    fileName = f"gen{population.generationNumber}.svg"
    filePath = join(
      self.persistenceFolder,
      fileName
    )

    with open(filePath, "w") as outFile:
      saveMiniaturesSvg(outFile, population.individuals, True)

class PicklePersistenceService(IPersistenceService):
  def save(self, population: Population) -> None:
    ...
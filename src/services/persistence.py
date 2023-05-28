from sre_constants import ANY_ALL
from typing import Any
from abc import ABC, abstractmethod
from core.population import Population
from services.service import Service

class IPersistenceService(Service):
  def __init__(self, persistenceFolder: str):
    self.persistenceFolder = persistenceFolder
    
  @abstractmethod
  def save(self, population: Population) -> Any:
    ...

class StubPersistenceService(IPersistenceService):
  def save(self, population: Population) -> None:
    return


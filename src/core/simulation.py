from typing import List
from services.plotters import *
from services.persistence import *

class Simulation:
  def __init__(self):
    self.plotterServices = list()
    self.persistenceServices = list()

  def withService(self, service: Service) -> Any:
    if isinstance(service, IPlotterService):
      self.plotterServices.add(service)
    elif isinstance(service, IPersistenceService):
      self.persistenceServices.add(service)

    return self
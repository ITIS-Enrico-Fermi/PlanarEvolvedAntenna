import logging
from typing import List
from services.plotters import *
from services.persistence import *
from services.statistics import *

class Simulation:
  def __init__(self, population: Population):
    self.population = population
    self.plotterServices: List[IPlotterService] = list()
    self.persistenceServices: List[IPersistenceService] = list()
    self.statServices: List[IStatService] = list()

  def withService(self, service: Service) -> Any:
    if isinstance(service, IPlotterService):
      target = self.plotterServices
    elif isinstance(service, IPersistenceService):
      target = self.persistenceServices
    elif isinstance(service, IStatService):
      target = self.statServices
    
    target.append(service)

    return self
  
  def runServices(self) -> None:
    for plotter in self.plotterServices:
      plotter.plot(self.population)
    
    for saver in self.persistenceServices:
      saver.save(self.population)
    
    for stater in self.statServices:
      stater.stat(self.population)
  
  def run(self, *_) -> None:
    generation, epoch = next(self.population.generations())

    logging.info(f"Epoch: {epoch}")
    logging.debug(generation)
    logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

    self.runServices()
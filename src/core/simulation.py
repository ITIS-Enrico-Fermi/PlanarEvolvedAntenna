import logging
from typing import List
from core.niche_population import NichePopulation
from services.service import *
from services.plotters import *
from services.persistence import *
from services.statistics import *

class Simulation:
  def __init__(self, population: Population, useNiches: bool = False, nichesActivationTh: float = 1):
    self.population = population
    self.plotterServices: List[IPlotterService] = list()
    self.persistenceServices: List[IPersistenceService] = list()
    self.statServices: List[IStatService] = list()
    self.liveViewers: List[ILiveViewService] = list()
    self.useNiches = useNiches
    self.nichesActivationTh = nichesActivationTh
    self.nicheEn = False

  def withService(self, service: Service) -> Any:
    if isinstance(service, IPlotterService):
      target = self.plotterServices
    elif isinstance(service, IPersistenceService):
      target = self.persistenceServices
    elif isinstance(service, IStatService):
      target = self.statServices
    elif isinstance(service, ILiveViewService):
      target = self.liveViewers
    
    if target is None:
      raise ServiceNotDispatched("Unhandled service added to simulation. Manage it for proper working")
    
    target.append(service)

    return self
  
  def runServices(self) -> None:
    for plotter in self.plotterServices:
      plotter.plot(self.population)
    
    for saver in self.persistenceServices:
      saver.save(self.population)
    
    for stater in self.statServices:
      stater.stat(self.population)

    for viewer in self.liveViewers:
      viewer.update(self.population)
  
  def run(self, *_) -> None:
    if self.useNiches and not self.nicheEn and self.population.fitnessMean > self.nichesActivationTh:
      self.population = NichePopulation().fromPopulation(self.population)
      self.nicheEn = True
    
    generation, epoch = next(self.population.generations())

    logging.info(f"Epoch: {epoch}")
    logging.debug(generation)
    logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

    self.runServices()
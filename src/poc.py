import argparse, logging
import signal, os
from typing import Callable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from rf.radiation import RadiationPattern
from services.plotters import *
from services.persistence import *
from services.statistics import *
from core.config import Config
from core.population import Population
from core.niche_population import NichePopulation
from core.simulation import Simulation
from multiprocessing import Pool
from functools import partial
from scipy.io import savemat

CONFIG_FILENAME = "config.yaml"

def main(doPlot: bool, doPlotWorld: bool, graphicsOutdir: str, withBoundaries: bool, statService: IStatService, instanceNumber: int = 0):
  signal.signal(signal.SIGINT, lambda *_: quit())

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

  
  PLOT_ROWS = 2
  PLOT_COLS = 3
  mainFig = plt.figure(f"Simulation {instanceNumber}")
  shape = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 1)
  radPatternSag = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 2, projection='polar')
  radPatternFront = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 3, projection='polar')
  fitnessGraph = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 4)
  killedGraph = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 5)
  distanceGraph = mainFig.add_subplot(PLOT_ROWS, PLOT_COLS, 6)
  mainFig.tight_layout()

  PersistenceServiceClass = StubPersistenceService
  if graphicsOutdir:
    if withBoundaries:
      PersistenceServiceClass = MiniatureWithBoundariesPersistenceService
    else:
      PersistenceServiceClass = MiniaturePersistenceService
  
  worldView = StubLiveViewService(None)
  if doPlotWorld:
    worldView = WorldLiveViewer(plt.figure(f"World Live View {instanceNumber}"), 20)

  statService.withGraphers(
    FitnessPlotter(fitnessGraph),
    KilledGenesPlotter(killedGraph),
    EuclideanDistancePlotter(distanceGraph)
  )

  if Config.GeneticAlgoTuning.useNiches:
    pop = NichePopulation()
  else:
    pop = Population()

  sim = Simulation(pop) \
    .withService(PlanarShapePlotter(shape)) \
    .withService(RadiationPatternPlotter(radPatternFront, Gene.getRadiationPatternFrontal)) \
    .withService(RadiationPatternPlotter(radPatternSag, Gene.getRadiationPatternSagittal)) \
    .withService(PersistenceServiceClass(graphicsOutdir)) \
    .withService(statService) \
    .withService(worldView)

  try:
    if doPlot:
      anim = animation.FuncAnimation(mainFig, sim.run, interval = 10, cache_frame_data = False)
      plt.show()
    else:
      while True:
        sim.run()
  except StopIteration:
    return statService.valuesDict
  
  return statService.valuesDict


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description = "Planar evolved antenna proof-of-concept"
  )

  parser.add_argument(
      "-p", "--plot", help="View what's happening in the simulation",
      default=False, action="store_true"
  )

  parser.add_argument(
    "-vw", "--view-world", help="Live view of simulation's world",
    default=False, action="store_true"
  )

  parser.add_argument(
    "-go", "--graphics-outdir", help="Graphics output folder. Save each generation to an svg file inside outdir. May slow down the simulation.",
    type=str, default=None
  )
  
  parser.add_argument(
    "-b", "--with-boundaries", help="Each gene in the svg file will have an underling path representing boundaries.",
    default=False, action="store_true"
  )

  parser.add_argument(
    "-so", "--stats-outdir", help="Specify stats output folder.",
    type=str, default=None
  )

  parser.add_argument(
    "-bm", "--benchmark-instances", help="Number of benchmark's paralell simulations",
    type=int, default=1
  )

  args = parser.parse_args()

  statsOutdir = args.stats_outdir
  if statsOutdir:
    StatServiceClass = StatService
  else:
    StatServiceClass = StubStatService
    statsOutdir = ""

  statServices = [StatServiceClass(join(statsOutdir, f"stats{i}.mat")) for i in range(args.benchmark_instances)]

  parallelMain = partial(main, args.plot, args.view_world, args.graphics_outdir, args.with_boundaries)
  with Pool(args.benchmark_instances) as p:
    statsDicts = p.starmap(parallelMain, [(statService, i) for i, statService in enumerate(statServices)])

  outStats = {}
  minLength = min([len(d['timeline']) for d in statsDicts])
  for statName in statsDicts[0].keys():
    rawValues = None

    for d in statsDicts:
      if rawValues is not None:
        rawValues = np.vstack((rawValues, d[statName][:minLength]))
      else:
        rawValues = np.array(d[statName][:minLength])
    
    outStats[statName] = np.mean(rawValues, axis=0)

  savemat(join("results", "aggregate_stats.mat"), outStats)

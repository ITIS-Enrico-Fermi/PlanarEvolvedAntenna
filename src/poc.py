import argparse, logging
import signal, os
from typing import Callable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from rf.radiation import RadiationPattern
from services.plotters import *
from services.persistence import *
from services.statistics import *
from utils.amenities import plotPathAndRad, saveSvg
from core.config import Config
from core.population import Population
from core.simulation import Simulation
from functools import partial

CONFIG_FILENAME = "config.yaml"

def main(doPlot: bool, outdir: str, withBoundaries: bool):
  signal.signal(signal.SIGINT, lambda *_: quit())

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

  if outdir is None:
    persistenceServiceClass = StubPlotterService
  else:
    if withBoundaries:
      persistenceServiceClass = MiniatureWithBoundariesPersistenceService
    else:
      persistenceServiceClass = MiniaturePersistenceService
  
  persistenceService = persistenceServiceClass(outdir)
  
  PLOT_ROWS = 2
  PLOT_COLS = 3
  fig = plt.figure()
  shape = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 1)
  radPatternSag = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 2, projection='polar')
  radPatternFront = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 3, projection='polar')
  fitnessGraph = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 4)
  killedGraph = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 5)
  distanceGraph = fig.add_subplot(PLOT_ROWS, PLOT_COLS, 6)
  fig.tight_layout()

  statService = StatService(join("results", "stats.mat")).withGraphers(
    FitnessPlotter(fitnessGraph),
    KilledGenesPlotter(killedGraph),
    EuclideanDistancePlotter(distanceGraph)
  )

  pop = Population()
  sim = Simulation(pop) \
    .withService(PlanarShapePlotter(shape)) \
    .withService(RadiationPatternPlotter(radPatternFront, Gene.getRadiationPatternFrontal)) \
    .withService(RadiationPatternPlotter(radPatternSag, Gene.getRadiationPatternSagittal)) \
    .withService(persistenceService) \
    .withService(statService)

  try:
    if doPlot:
      anim = animation.FuncAnimation(fig, sim.run, interval = 10, cache_frame_data = False)
      plt.show()
    else:
      while True:
        sim.run()
  except StopIteration:
    quit()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description = "Planar evolved antenna proof-of-concept"
  )

  parser.add_argument(
    "-p", "--plot", help="View what's happening in the simulation",
    default=False, action="store_true"
  )

  parser.add_argument(
    "-o", "--outdir", help="Save each generation to an svg file inside outdir. May slow down the simulation.",
    type=str, default=None
  )
  
  parser.add_argument(
    "-b", "--with-boundaries", help="Each gene in the svg file will have an underling path representing boundaries.",
    default=False, action="store_true"
  )

  args = parser.parse_args()

  main(args.plot, args.outdir, args.with_boundaries)
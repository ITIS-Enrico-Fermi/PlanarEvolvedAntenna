import argparse
import logging
import signal
from utils.amenities import plotPath
from config import Config
from population import Population
from functools import partial
from typing import Callable

CONFIG_FILENAME = "config.yaml"

def simulationStep(pop: Population, doPlot: bool, *_) -> None:
  generation, epoch = next(pop.generations())
  
  logging.info(f"Epoch: {epoch}")
  logging.debug(generation)
  logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

  if doPlot:
    plotPath(f"Epoch: {epoch} - Fitness: {generation[0].fitness():.2f}", generation[0].getCartesianCoords())  # Plot only best performing individual


def buildSimulation(doPlot: bool, *_) -> Callable[[Population, bool], None]:
  pop = Population()

  signal.signal(signal.SIGINT, lambda *_: print(f"King is: {pop.king}"))

  return partial(simulationStep, pop, doPlot)


def main(doPlot: bool):

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

  simulation = buildSimulation(doPlot)
    
  if doPlot:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    fig = plt.figure()
    anim = animation.FuncAnimation(fig, simulation, interval=10)
    plt.show()

  else:
    while True:
      simulation()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description = "Planar evolved antenna proof-of-concept"
  )

  parser.add_argument(
    "-p", "--plot", help="View what's happening in the simulation",
    default=False, action="store_true"
  )

  args = parser.parse_args()

  main(args.plot)
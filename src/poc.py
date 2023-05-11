import argparse
import logging
import signal
from utils.amenities import plotPath
from config import Config
from population import Population
from functools import partial
from typing import Callable

CONFIG_FILENAME = "config.yaml"

def simulationStep(pop: Population, doPlot: bool, shape_axes, radiation_axes, *_) -> None:
  generation, epoch = next(pop.generations())
  
  logging.info(f"Epoch: {epoch}")
  logging.debug(generation)
  logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

  if doPlot:
    plotPath(
      title=f"Epoch: {epoch} - Fitness: {generation[0].fitness():.2f}",
      polychain=generation[0].getCartesianCoords(),  # Plot only best performing individual
      radiation=generation[0].getRadiationPattern(),
      axes=(shape_axes, radiation_axes)
    )


def buildSimulation(doPlot: bool, *args) -> Callable[[Population, bool], None]:
  pop = Population()

  signal.signal(signal.SIGINT, lambda *_: print(f"King is: {pop.king}"))

  return partial(simulationStep, pop, doPlot, *args)


def main(doPlot: bool):

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

    
  if doPlot:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    fig = plt.figure()
    shape = fig.add_subplot(1, 2, 1)
    radPattern = fig.add_subplot(1, 2, 2, projection='polar')
    simulation = buildSimulation(doPlot, shape, radPattern)
    anim = animation.FuncAnimation(fig, simulation, interval=10)
    plt.show()

  else:
    simulation = buildSimulation(doPlot)
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
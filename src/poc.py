import argparse
import logging
import signal
from typing import Callable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.amenities import plotPath
from config import Config
from population import Population
from functools import partial

CONFIG_FILENAME = "config.yaml"

def simulationStep(
  pop: Population,
  doPlot: bool,
  *_,
  **kwargs) -> None:
  try:
    generation, epoch = next(pop.generations())
  except StopIteration:
    return

  logging.info(f"Epoch: {epoch}")
  logging.debug(generation)
  logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

  if doPlot:
    plotPath(
      title=f"Epoch: {epoch} - Fitness: {generation[0].fitness():.2f}",
      polychain=generation[0].getCartesianCoords(),  # Plot only best performing individual
      radiation=generation[0].getRadiationPattern(),
      axes=(kwargs.pop("shapeAxes"), kwargs.pop("radiationAxes"))
    )
  
  outputDirectory = kwargs.pop("outputDirectory")
  if outputDirectory is not None:
    print(outputDirectory)


def buildSimulation(doPlot: bool, *_, **kwargs) -> Callable[[Population, bool], None]:
  pop = Population()

  signal.signal(signal.SIGINT, lambda *_: print(f"King is: {pop.king}"))

  return partial(simulationStep, pop, doPlot, **kwargs)


def main(doPlot: bool, outdir: str):

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)
    
  if doPlot:
    fig = plt.figure()
    shape = fig.add_subplot(1, 2, 1)
    radPattern = fig.add_subplot(1, 2, 2, projection='polar')
    simulation = buildSimulation(doPlot, shapeAxes = shape, radiationAxes = radPattern, outputDirectory = outdir)
    anim = animation.FuncAnimation(fig, simulation, interval=10, cache_frame_data=False)
    plt.show()
    
  else:
    simulation = buildSimulation(doPlot, outputDirectory = outdir)
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

  parser.add_argument(
    "-o", "--outdir", help="Save each generation to an svg file inside outdir. May slow down the simulation.",
    type=str, default=None
  )

  args = parser.parse_args()

  main(args.plot, args.outdir)
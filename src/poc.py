import argparse, logging
import signal, os
from typing import Callable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.amenities import plotPathAndRad, saveSvg
from config import Config
from core.population import Population
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
    quit()

  logging.info(f"Epoch: {epoch}")
  logging.debug(generation)
  logging.info(f"Best gene (fitness={generation[0].fitness():.2f}):\n{generation[0]}")

  if doPlot:
    plotPathAndRad(
      title = f"Epoch: {epoch} -\n"
        f"Best fitness: {generation[0].fitness():.2f} -\n"
        f"Mean fitness: {pop.fitnessMean:.2f} -\n"
        f"Sd fitness: {pop.fitnessStdDev:.2f}",
      polychain = generation[0].getCartesianCoords(),  # Plot only best performing individual
      radiationSagittal = generation[0].getRadiationPatternSagittal(),
      radiationFrontal = generation[0].getRadiationPatternFrontal(),
      groundPlaneDistance = generation[0].groundPlaneDistance,
      axes = (kwargs.pop("shapeAxes"), kwargs.pop("radiationAxesSag"), kwargs.pop("radiationAxesFront"))
    )
  
  outputDirectory = kwargs.pop("outputDirectory")
  if outputDirectory is not None:
    with open(os.path.join(outputDirectory, f"gen{epoch}.svg"), "w") as outFile:
      saveSvg(outFile, generation, kwargs.pop("withBoundaries"))


def buildSimulation(doPlot: bool, *_, **kwargs) -> Callable[[Population, bool], None]:
  pop = Population()

  signal.signal(signal.SIGINT, lambda *_: quit())

  return partial(simulationStep, pop, doPlot, **kwargs)


def main(doPlot: bool, outdir: str, withBoundaries: bool):

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
  )

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)
    
  if doPlot:
    fig = plt.figure()
    shape = fig.add_subplot(1, 3, 1)
    radPatternSag = fig.add_subplot(1, 3, 2, projection='polar')
    radPatternFront = fig.add_subplot(1, 3, 3, projection='polar')
    simulation = buildSimulation(
      doPlot,
      shapeAxes = shape,
      radiationAxesSag = radPatternSag,
      radiationAxesFront = radPatternFront,
      outputDirectory = outdir,
      withBoundaries = withBoundaries
    )
    anim = animation.FuncAnimation(fig, simulation, interval=10, cache_frame_data=False)
    plt.show()
    
  else:
    simulation = buildSimulation(doPlot, outputDirectory = outdir, withBoundaries = withBoundaries)
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
  
  parser.add_argument(
    "-b", "--with-boundaries", help="Each gene in the svg file will have an underling path representing boundaries.",
    default=False, action="store_true"
  )

  args = parser.parse_args()

  main(args.plot, args.outdir, args.with_boundaries)
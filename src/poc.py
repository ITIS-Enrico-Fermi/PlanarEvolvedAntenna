import argparse
from utils.amenities import plotPath
from config import Config
from population import Population
from functools import partial
from typing import Callable

CONFIG_FILENAME = "config.yaml"

def simulationStep(pop: Population, doPlot: bool, *_) -> None:
  generation, epoch = next(pop.generations())

  print(epoch, generation)

  if doPlot:
    plotPath(f"Epoch: {epoch}", generation[0].getCartesianCoords())  # Plot only best performing individual

  return


def buildSimulation(doPlot: bool, *_) -> Callable[[Population, bool], None]:
  pop = Population()

  return partial(simulationStep, pop, doPlot)


def main(doPlot: bool):
  epochs = 20

  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

  simulation = buildSimulation(doPlot)
    
  if doPlot:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    simulation_callback = partial(simulation, doPlot)

    fig = plt.figure()
    anim = animation.FuncAnimation(fig, simulation, interval=200)
    plt.show()

  else:
    for e in range(epochs):
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
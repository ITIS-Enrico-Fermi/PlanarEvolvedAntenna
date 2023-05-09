import argparse
from utils import plotPath
from config import Config
from population import Population

CONFIG_FILENAME = "config.yaml"

def main(doPlot: bool):
  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)
    
  pop = Population()
  for generation, epoch in pop.nextGeneration():
    print(epoch, generation)

    if doPlot:
      import matplotlib.pyplot as plt
      plotPath(f"Epoch: {epoch}", sorted(generation)[0].getPolarCoords())  # Plot only best performing individual


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
import math
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from typing import List, Tuple, IO, Any
from config import Config
from utils.geometry import *
from rf.radiation import RadiationPattern


def plotCansatBottomProfile(axes: plt.Axes):
  SAFE_MARGIN = 0.05
  outerRadius = Config.ShapeConstraints.outerDiam / 2
  outerCircle = plt.Circle((0, 0), outerRadius, color='#ffcdd2')
  axes.set_xlim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
  axes.set_ylim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
  axes.add_patch(outerCircle)
  
  innerRadius = Config.ShapeConstraints.innerDiam / 2
  innerCircle = plt.Circle((Config.ShapeConstraints.centerShift, 0), innerRadius, color='#000000')
  axes.add_patch(innerCircle)

def plotAntennaPath(axes: plt.Axes, polychain: List[Segment], color: str = "#4caf50", width: int = 3):
  lines = [line.toList() for line in polychain]
  lineCollection = mc.LineCollection(lines, linewidths=width, color=color)
  axes.add_collection(lineCollection)

def plotRadiationPatternSlice(axes: plt.Axes, radiation: RadiationPattern):
  axes.plot(radiation.thetasRad, radiation.gainsMw)

def plotPathAndRad(title: str, polychain: List[Segment], radiationSagittal: RadiationPattern, radiationFrontal: RadiationPattern, axes: Tuple[plt.Axes, plt.Axes, plt.Axes]) -> None:
  ax, radiSag, radiFront = axes
  ax.axis("equal")
  ax.clear()
  radiSag.clear()
  radiFront.clear()

  plotCansatBottomProfile(ax)
  plotAntennaPath(ax, polychain)
  plotRadiationPatternSlice(radiSag, radiationSagittal)
  plotRadiationPatternSlice(radiFront, radiationFrontal)

  plt.title(title)

def saveSvg(stream: IO[Any], generation: List[List[PolarCoord]], doPlotConstraints: bool):
  fig = plt.figure()
  edgeLen = math.floor(math.sqrt(len(generation)))
  axes = fig.subplots(edgeLen, edgeLen)

  for i in range(edgeLen):
    for j in range(edgeLen):
      idx = edgeLen * i + j
      axes[i][j].axis("equal")
      axes[i][j].axis("off")
      if doPlotConstraints:
        plotCansatBottomProfile(axes[i][j])
        pathColor = "#4caf50"
      else:
        pathColor = "#000000"
      plotAntennaPath(axes[i][j], generation[idx].getCartesianCoords(), pathColor, 1)
      axes[i][j].autoscale()

  plt.savefig(stream, format="svg")
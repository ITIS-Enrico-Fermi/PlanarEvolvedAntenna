import matplotlib.pyplot as plt
import matplotlib.collections as mc
from typing import List, Tuple
from config import Config
from utils.geometry import *
from rf.radiation import RadiationPattern

def plotPath(title: str, polychain: List[Segment], radiation: RadiationPattern, axes: Tuple[plt.Axes, plt.Axes]) -> None:
  ax, radi = axes
  ax.axis("equal")

  def plotCansatBottomProfile():
    SAFE_MARGIN = 0.05
    outerRadius = Config.ShapeConstraints.outerDiam / 2
    outerCircle = plt.Circle((0, 0), outerRadius, color='#ffcdd2')
    ax.set_xlim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
    ax.set_ylim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
    ax.add_patch(outerCircle)
    
    innerRadius = Config.ShapeConstraints.innerDiam / 2
    innerCircle = plt.Circle((Config.ShapeConstraints.centerShift, 0), innerRadius, color="#000000")
    ax.add_patch(innerCircle)
  
  def plotAntennaPath():
    lines = [line.toList() for line in polychain]
    lineCollection = mc.LineCollection(lines, linewidths=3, color="#4caf50")
    ax.add_collection(lineCollection)

  def plotRadiationPattern():
    radi.plot(radiation.thetas, radiation.gains_db)

  ax.clear()
  radi.clear()
  plotCansatBottomProfile()
  plotAntennaPath()
  plotRadiationPattern()

  plt.savefig(f"results/out.svg")
  plt.title(title)

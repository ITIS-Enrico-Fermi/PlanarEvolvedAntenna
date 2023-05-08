from asyncio import start_server
from cmath import polar
from operator import length_hint
from turtle import circle
import numpy as np
from config import Config
from typing import List, Tuple

class PolarCoord:
  def __init__(self, angle: float, distance: float):
    self.angle = angle
    self.distance = distance
  
  def __repr__(self):
    return f"[Angle: {self.angle}, Dist: {self.distance}]"
  
class Point:
  def __init__(self, x: float, y: float):
    self.x = x
    self.y = y
  
  def __repr__(self):
    return f"({self.x}, {self.y})"

class Segment:
  def __init__(self, start: Point, end: Point):
    self.start = start
    self.end = end
  
  def __repr__(self):
    return f"<{self.start} - {self.end}>"
  
  def toList(self) -> List[Tuple[float, float]]:
    return [(self.start.x, self.start.y), (self.end.x, self.end.y)]

def plotPath(title: str, polarCoords: List[Tuple[float, float]]) -> None:
  import matplotlib.pyplot as plt
  import matplotlib.collections as mc
  
  fig, ax = plt.subplots()
  ax.axis("equal")

  def plotCansatBottomProfile():
    SAFE_MARGIN = 0.05
    outerRadius = Config.ShapeConstraints.outerDiam / 2
    outerCircle = plt.Circle((0, 0), outerRadius, color='#ffcdd2')
    ax.set_xlim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN*outerRadius))
    ax.set_ylim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN*outerRadius))
    ax.add_patch(outerCircle)
    
    innerRadius = Config.ShapeConstraints.innerDiam / 2
    innerCircle = plt.Circle((Config.ShapeConstraints.centerShift, 0), innerRadius, color="#bbdefb")
    ax.add_patch(innerCircle)
  
  def plotAntennaPath():
    FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)
    segments: List[Segment] = [
      Segment(
        FIRST_POINT,
        polarToCart(FIRST_POINT, polarCoords[0])
    )]

    for i in range(1, len(polarCoords) - 1):
      segments.append(
        Segment(
          segments[i-1].end, polarToCart(segments[i-1].end, polarCoords[i]))
      )
    
    lines = [line.toList() for line in segments]
    lineCollection = mc.LineCollection(lines, linewidths=3)
    ax.add_collection(lineCollection)

  plotCansatBottomProfile()
  plotAntennaPath()

  plt.show()

def polarToCart(startPoint: Point, polarCoord: PolarCoord) -> Point:
  """Takes a start point and a polar coord to compute the segment's end point
  
  :param startPoint: a Point representing a cartesian coordinate
  :param polarCoord: a PolarCoord representing a polar coordinate

  :returns: end point of the segments connecting startPoint + polarCoord
  """
  return Point(
    startPoint.x + np.cos(polarCoord.angle) * polarCoord.distance,
    startPoint.y + np.sin(polarCoord.angle) * polarCoord.distance
  )
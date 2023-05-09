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
  
  def __getitem__(self, idx) -> float:
    if (idx < 0 or idx > 1):
      raise IndexError("Out of range")
    
    return self.angle if idx == 0 else self.distance
  
class Point:
  def __init__(self, x: float, y: float):
    self.x = x
    self.y = y
  
  def __repr__(self) -> str:
    return f"({self.x}, {self.y})"
  
  def __add__(self, other) -> Point:
    return Point(self.x + other.x, self.y + other.y)

class Segment:
  def __init__(self, start: Point, end: Point):
    self.start = start
    self.end = end
  
  def __repr__(self) -> str:
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
    FIRST_POINT_CART = Point(- Config.ShapeConstraints.outerDiam / 2, 0)
    segments: List[Segment] = [
      Segment(
        FIRST_POINT_CART,
        FIRST_POINT_CART + polarToCart(polarCoords[0])
    )]

    for i in range(1, len(polarCoords) - 1):
      segments.append(
        Segment(
          segments[i-1].end, segments[i-1].end + polarToCart(polarCoords[i]))
      )
    
    lines = [line.toList() for line in segments]
    lineCollection = mc.LineCollection(lines, linewidths=3, color="#4caf50")
    ax.add_collection(lineCollection)

  plotCansatBottomProfile()
  plotAntennaPath()

  plt.show()

def polarToCart(polarCoord: PolarCoord) -> Point:
  return Point(
    np.cos(polarCoord.angle) * polarCoord.distance,
    np.sin(polarCoord.angle) * polarCoord.distance
  )

def isSelfIntersectingPath(polarCoords: List[PolarCoord]) -> bool:
  # See Bentley-Ottmann for a generic approach
  segmentList = []

  p1 = Point(0, 0)
  for pc in polarCoords:
    p2 = p1 + polarToCart(pc)
    segmentList.append(Segment(p1, p2))
    p1 = p2
  
  for i in range(len(segmentList)):
    for j in range(i+1, len(segmentList)):
      if areIntersectingSegments(segmentList[i], segmentList[j]):
        return True
  
  return False

def areIntersectingSegments(segment1: Segment, segment2: Segment) -> bool:
  return (
    areIntersectingIntervals((segment1.start.x, segment1.end.x), (segment2.start.x, segment2.end.x)) and
    areIntersectingIntervals((segment1.start.y, segment1.end.y), (segment2.start.y, segment2.end.y))
  )

def areIntersectingIntervals(interval1: Tuple[float, float], interval2: Tuple[float, float]) -> bool:
  return (
    interval2[0] <= interval1[1] <= interval2[1] or
    interval2[0] <= interval1[0] <= interval2[1] or
    interval1[0] <= interval2[1] <= interval1[1] or
    interval1[0] <= interval2[0] <= interval1[1]
  )
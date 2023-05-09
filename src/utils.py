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
  
  def __add__(self, other):
    return Point(self.x + other.x, self.y + other.y)

class Segment:
  def __init__(self, start: Point, end: Point):
    self.start = start
    self.end = end
  
  def __repr__(self) -> str:
    return f"<{self.start} - {self.end}>"
  
  def toList(self) -> List[Tuple[float, float]]:
    return [(self.start.x, self.start.y), (self.end.x, self.end.y)]


def plotPath(title: str, polarCoords: List[PolarCoord]) -> None:
  import matplotlib.pyplot as plt
  import matplotlib.collections as mc
  
  fig, ax = plt.subplots()
  ax.axis("equal")

  def plotCansatBottomProfile():
    SAFE_MARGIN = 0.05
    outerRadius = Config.ShapeConstraints.outerDiam / 2
    outerCircle = plt.Circle((0, 0), outerRadius, color='#ffcdd2')
    ax.set_xlim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
    ax.set_ylim((-outerRadius - SAFE_MARGIN*outerRadius, outerRadius + SAFE_MARGIN * outerRadius))
    ax.add_patch(outerCircle)
    
    innerRadius = Config.ShapeConstraints.innerDiam / 2
    innerCircle = plt.Circle((Config.ShapeConstraints.centerShift, 0), innerRadius, color="#bbdefb")
    ax.add_patch(innerCircle)
  
  def plotAntennaPath():
    FIRST_POINT = Point(- Config.ShapeConstraints.outerDiam / 2, 0)
    rodCoords = polarToRod(polarCoords)
    segments = rodToPolyChain(FIRST_POINT, rodCoords)
    lines = [line.toList() for line in segments]
    lineCollection = mc.LineCollection(lines, linewidths=3, color="#4caf50")
    ax.add_collection(lineCollection)

  plotCansatBottomProfile()
  plotAntennaPath()

  plt.show()

def polarToRod(polarCoords: List[PolarCoord]) -> List[PolarCoord]:
  rodCoords = [polarCoords[0]]

  for i in range(1, len(polarCoords)):
    rodCoords.append(
      PolarCoord(
        rodCoords[i-1].angle + polarCoords[i].angle,
        polarCoords[i].distance
    ))
  
  return rodCoords

def rodToPolyChain(startPoint: Point, rodCoords: List[PolarCoord]) -> List[Segment]:
  segments = []

  p1 = startPoint
  for rc in rodCoords:
    p2 = p1 + polarToCart(rc)
    segments.append(Segment(p1, p2))
    p1 = p2
  
  return segments

def polarToCart(polarCoord: PolarCoord) -> Point:
  return Point(
    np.cos(polarCoord.angle) * polarCoord.distance,
    np.sin(polarCoord.angle) * polarCoord.distance
  )

def isSelfIntersectingPath(polarCoords: List[PolarCoord]) -> bool:
  # See Bentley-Ottmann for a generic approach
  segmentList = rodToPolyChain(
    Point(0, 0),
    polarToRod(polarCoords)
  )
  
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
  a1 = min(interval1[0], interval1[1])
  a2 = max(interval1[0], interval1[1])

  b1 = min(interval2[0], interval2[1])
  b2 = max(interval2[0], interval2[1])

  return (
    a1 < b1 < a2 or
    a1 < b2 < a2 or
    b1 < a1 < b2 or
    b1 < a2 < b2
  )
import numpy as np
from typing import List, Tuple
from itertools import tee
from core.config import Config

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
        return f"<{self.start}, {self.end}>"
    
    def toList(self) -> List[Tuple[float, float]]:
        return [(self.start.x, self.start.y), (self.end.x, self.end.y)]
    
Polychain = List[Segment]

def cartesianToPolychain(coords: List[Tuple]) -> Polychain:
    lx, dx = tee(coords)
    next(dx)

    return [Segment(Point(*p1), Point(*p2)) for p1, p2 in zip(lx, dx)]

def polychainToCartesian(chain: Polychain) -> List[Point]:
    coords = [p.start for p in chain]
    coords.append(chain[-1].end)

    return coords

def rodToPolar(rodCoords: List[PolarCoord]) -> List[PolarCoord]:
    polarCoords = [rodCoords[0]]

    for i in range(1, len(rodCoords)):
        polarCoords.append(
            PolarCoord(
                polarCoords[i-1].angle + rodCoords[i].angle,
                rodCoords[i].distance
        ))
    
    return polarCoords

def polarToPolychain(startPoint: Point, polarCoords: List[PolarCoord]) -> List[Segment]:
    segments = []

    p1 = startPoint
    for rc in polarCoords:
        p2 = p1 + Point(*polarToCart(rc.distance, rc.angle))
        segments.append(Segment(p1, p2))
        p1 = p2
    
    return segments

def polarToCart(distance: float, angle: float) -> Tuple:
    return (
        np.cos(angle) * distance,
        np.sin(angle) * distance
    )

def isSelfIntersectingPath(polychain: List[Segment]) -> bool:
    # See Bentley-Ottmann for a generic approach
    for i in range(len(polychain)):
        for j in range(i+1, len(polychain)):
            if areIntersectingSegments(polychain[i], polychain[j]):
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

def isPathInCircle(polychain: List[Segment], center: Point, radius: float) -> bool:
    # Most likely to found segments out of the circle at the end of the path
    radiusSquared = radius**2

    for segment in reversed(polychain):
        if segment.end.x**2 + segment.end.y**2 > radiusSquared:
            return False
    
    return True

def doesPathIntersectCircle(polychain: List[Segment], center: Point, radius: float) -> bool:
    # Square approximation
    mainDiag = Segment(
        Point(center.x - radius, center.y - radius),
        Point(center.x + radius, center.y + radius)
    )

    secondaryDiag = Segment(
        Point(center.x + radius, center.y + radius),
        Point(center.x - radius, center.y - radius)
    )


    for segment in reversed(polychain):
        if areIntersectingSegments(segment, mainDiag) or \
            areIntersectingSegments(segment, secondaryDiag):
            return True
    
    return False

def randomPointsInsideCircle(numberOfPoints: int, circleRadius: float) -> np.ndarray[Tuple]:
    x = np.random.uniform(-circleRadius, circleRadius, numberOfPoints)
    x = np.sort(x)
    y = np.random.uniform(-circleRadius, circleRadius, numberOfPoints)

    points = np.column_stack((x, y))

    return points

def randomPointsRod(config: Config.GeneEncoding) -> np.ndarray[Tuple]:
    lengths = np.random.uniform(config.minSegmentLen, config.maxSegmentLen, config.segmentsNumber)
    angles = np.random.uniform(-np.pi/config.segmentsNumber, np.pi/config.segmentsNumber, config.segmentsNumber)

    rodEncoding = list(zip(angles, lengths))
    rodEncoding = [PolarCoord(a, l) for (a, l) in rodEncoding]

    polychain = polarToPolychain(Point(-33, 0), rodToPolar(rodEncoding))    #TODO: extract -33 as parameter

    points = polychainToCartesian(polychain)

    return np.array([(p.x, p.y) for p in points])
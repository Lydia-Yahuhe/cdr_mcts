from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from typing import List
from ..geom import Point2D


Inclusion = Enum("Inclusion", ('In', 'Out'))


@dataclass
class Location:
    id: str
    location: Point2D

    def distance_to(self, other: Location) -> float:
        return self.location.distance_to(other.location)

    def bearing(self, other: Location):
        return self.location.bearing(other.location)


@dataclass
class Waypoint(Location):
    def __str__(self): 
        return '[%s, %s]'%(self.id, self.location)

    def __repr__(self):
        return '[%s, %s]'%(self.id, self.location)

    
@dataclass
class ATSRoute(object):
    id:str
    waypoints: []


@dataclass
class Polygon(object):
    id:str
    points: []


@dataclass
class Block(object):
    id: str
    minAlt:float
    maxAlt: float
    polygon: Polygon


@dataclass
class BlockInclusion(object):
    block: Block
    inclusion: Inclusion = Inclusion.In


@dataclass
class ATCSector(object):
    id: str
    blocks: []
    activateTimes: []


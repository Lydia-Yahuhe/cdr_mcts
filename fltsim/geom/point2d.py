from __future__ import annotations
from dataclasses import dataclass
from . import util


@dataclass
class Point2D(object):
    lng: float = 0.0
    lat: float = 0.0

    def reset(self, other: Point2D):
        self.lng = other.lng
        self.lat = other.lat

    def set(self, other: Point2D):
        self.lng = other.lng
        self.lat = other.lat

    def toArray (self):
        return [self.lng, self.lat]

    def toTuple(self):
        return (self.lng, self.lat)

    def clear(self):
        self.lng = 0
        self.lat = 0

    def distance_to(self, other: Point2D):
        return util.distance_point2d(self, other)

    def bearing(self, other: Point2D):
        return util.bearing_point2d(self, other)

    def destination(self, course: float, dist: float):
        coords = util.destination(self.toTuple(), course, dist)
        return Point2D(coords[0], coords[1])
        
    def move(self, course: float, dist: float):
        util.move_point2d(self, course, dist)

    def copy(self):
        return Point2D(self.lng, self.lat)

    def __str__(self):
        return '<%.5f,%.5f>'%(self.lng, self.lat)

    def __repr(self):
        return '<%.5f,%.5f>'%(self.lng, self.lat)

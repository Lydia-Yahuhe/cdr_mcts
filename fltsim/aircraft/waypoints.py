from __future__ import annotations
from dataclasses import dataclass, field
from .. import model
from ..geom import Point2D

idgen = 0


@dataclass
class LngLatWaypoint(model.Waypoint):
    pass


# ATOWaypoint along-track offset
@dataclass
class ATOWaypoint(model.Waypoint):
    ref: model.Waypoint


def create_atowaypoint2(ref: model.Waypoint, loc: Point2D) -> ATOWaypoint:
    return ATOWaypoint('Ref<%s>'%ref.id, loc, ref)


def create_lnglat_waypoint(lngLat) -> LngLatWaypoint:
    global idgen
    idgen += 1
    return LngLatWaypoint('WPT#%d'%idgen, lngLat)


def create_atowaypoint(ref: model.Waypoint, bearing: float, dist: float) -> ATOWaypoint:
    loc = Point2D(ref.location.lng, ref.location.lat)
    loc.move(bearing, dist)
    return ATOWaypoint('Ref<%s>'%ref.id, loc, ref)

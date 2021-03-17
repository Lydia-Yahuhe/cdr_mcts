from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from enum import Enum
from ..model import Routing, Waypoint, aircraftTypes, AircraftType, FlightPerformance, FlightPlan
from ..geom import Point2D
from . import atccmd


FPLPhase = Enum('FPLPhase', ('Schedule', 'EnRoute', 'Finished'))


@dataclass
class FlightControlData:
    altCmd: atccmd.AltCmd = None
    spdCmd: atccmd.SpdCmd = None
    offsetCmd: atccmd.LateralOffset = None

    def set(self, other: FlightControlData):
        self.altCmd = other.altCmd
        self.spdCmd = other.spdCmd
        self.offsetCmd = other.offsetCmd


@dataclass
class FlightGuidance:
    RFL: float = 0
    targetAlt: float = 0
    targetHSpd: float = 0
    targetCourse: float = 0

    def set(self, other: FlightGuidance):
        self.RFL = other.RFL
        self.targetAlt = other.targetAlt
        self.targetHSpd = other.targetHSpd
        self.targetCourse = other.targetCourse


@dataclass
class FlightLeg:
    start: Waypoint
    end: Waypoint
    distance: float = 0
    course: float = 0

    def __post_init__(self):
        self.distance = self.start.distance_to(self.end)
        self.course = self.start.bearing(self.end)

    def copy(self) -> FlightLeg:
        return FlightLeg(self.start, self.end)


@dataclass
class FlightProfile(object):
    originRoute: Routing = None
    fixedRoute: Routing = None
    offsetRoute: Routing = None
    offsetDistance: float = 0
    offsetInitialLegIdx: int = -1

    legs: List[FlightLeg] = None
    curLegIdx: int = 0
    curLeg: FlightLeg = None
    nextLeg: FlightLeg = None
    distToTarget: float = 0
    courseToTarget: float = 0

    @property
    def target(self) -> Waypoint:
        if not self.curLeg:
            return None
        return self.curLeg.end

    @property
    def nextTarget(self) -> Waypoint:
        if not self.nextLeg:
            return None
        return self.nextLeg.end

    @property
    def curRoute(self) -> Routing:
        if self.offsetRoute:
            return self.offsetRoute
        if self.fixedRoute:
            return self.fixedRoute
        return self.originRoute

    @property
    def next_four(self):
        wptList = self.originRoute.waypointList
        if self.offsetInitialLegIdx == -1:
            start_idx = self.curLegIdx
        else:
            start_idx = self.offsetInitialLegIdx

        end_idx = min(start_idx + 4, len(wptList) - 1)
        return wptList[start_idx: end_idx]

    def set(self, other: FlightProfile):
        self.originRoute = other.originRoute
        self.fixedRoute = copy_route(other.fixedRoute)
        self.offsetRoute = copy_route(other.offsetRoute)
        self.offsetDistance = other.offsetDistance
        self.offsetInitialLegIdx = other.offsetInitialLegIdx
        
        if not other.legs:
            self.legs = None
        else:
            self.legs = [leg for leg in other.legs]

        self.curLegIdx = other.curLegIdx
        self.curLeg = other.curLeg
        self.nextLeg = other.nextLeg
        self.distToTarget = other.distToTarget
        self.courseToTarget = other.courseToTarget

    def is_cancel_offset(self):
        return self.offsetRoute is not None and self.curLegIdx >= len(self.offsetRoute.waypointList) - 2


def copy_route(r: Routing) -> Routing:
    if not r:
        return None
    return Routing(r.id, [wpt for wpt in r.waypointList])


@dataclass
class PhsyData:
    hSpd: float = 0
    vSpd: float = 0
    alt: float = 0
    heading: float = 0
    acftType: AircraftType = aircraftTypes['A320']
    location: Point2D = field(default_factory=Point2D)
    performance: FlightPerformance = field(default_factory=FlightPerformance)

    @property
    def course(self):
        return self.heading

    def set(self, other: PhsyData):
        self.hSpd = other.hSpd
        self.vSpd = other.vSpd
        # pylint: disable=no-member
        self.location.reset(other.location)
        self.alt = other.alt
        self.heading = other.heading
        self.acftType = other.acftType
        # pylint: disable=no-member
        self.performance.copy(other.performance)
    
    def get_parts(self):
        return self.hSpd, self.vSpd, self.heading, self.acftType.id, self.performance.altitude


@dataclass
class FlightPlanData:
    curFPL: FlightPlan = None
    curFPLPhase: FPLPhase = FPLPhase.Schedule
    scheduledFPL: FlightPlan = field(default_factory=list)

    def set(self, other: FlightPlanData):
        self.curFPL = other.curFPL
        self.curFPLPhase = other.curFPLPhase
        self.scheduledFPL = other.scheduledFPL


@dataclass
class AircraftAgentData:
    __slots__ = ('id', 'time', 'fltCtr', 'fltCmd', 'phsyData', 'profile', 'fplData')

    def __init__(self, id, acftType, time=0):
        self.id = id
        self.time: int = time
        self.fltCtr = FlightControlData()
        self.fltCmd = FlightGuidance()
        self.phsyData = PhsyData(acftType=acftType)
        self.profile = FlightProfile()

    #
    def add_time(self) -> int:
        self.time += 1
        return self.time
    
    def set(self, other: AircraftAgentData):
        self.id = other.id
        self.time = other.time
        self.fltCmd.set(other.fltCmd)
        self.fltCtr.set(other.fltCtr)
        self.phsyData.set(other.phsyData)
        self.profile.set(other.profile)

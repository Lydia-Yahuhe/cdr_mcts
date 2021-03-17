from dataclasses import dataclass
from .aircrafttype import AircraftType
from typing import List, Dict
from .airspace import Waypoint


@dataclass
class Aircraft:
    id: str
    aircraftType: AircraftType
    airline: str = None


@dataclass
class Routing:
    id: str
    waypointList: List[Waypoint]
    start: int = 0


@dataclass
class FlightPlan:
    id: str
    RFL: float
    routing: Routing
    startTime: int
    aircraft: Aircraft
    alt: float
    cruise: int = 0


@dataclass
class DataSet:
    waypoints: Dict[str, Waypoint]
    routings: Dict[str, Routing]
    flightPlans: Dict[str, FlightPlan]
    aircrafts: Dict[str, Aircraft]


@dataclass
class ConflictSceneInfo:
    time: int
    pos: List[List[float]]
    conflict_ac: List[int]
    fpl_list: List[FlightPlan]

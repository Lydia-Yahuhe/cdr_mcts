from __future__ import annotations
import math

from fltsim.geom import Point2D
from fltsim.geom.util import move_point2d
from fltsim.model import Waypoint
from .. import model
from .waypoints import create_lnglat_waypoint
from . import atccmd
from .acft_data import FlightLeg

NM2M = 1852


def reset_flightprofile_with_fpl(profile, fpl):
    profile.originRoute = fpl.routing  # -
    profile.fixedRoute = fpl.routing
    profile.offsetDistance = 0
    profile.offsetRoute = None
    profile.offsetInitialLegIdx = -1

    profile.legs = make_leg_from_waypoint(fpl.routing.waypointList)  # -

    profile.curLegIdx = 0  # -
    profile.curLeg = profile.legs[0]  # -
    profile.distToTarget = profile.legs[0].distance  # -
    profile.courseToTarget = profile.legs[0].course  # -

    profile.nextLeg = profile.legs[1] if len(profile.legs) > 1 else None


def update_route(profile, phsyData, fltCtr, now: int):
    offset_cmd = fltCtr.offsetCmd
    if offset_cmd is None:
        return

    if profile.is_cancel_offset():
        cancel_offset(profile, phsyData)
        fltCtr.offsetCmd = None

    assign = offset_cmd.assignTime == now
    if assign:
        cancel_offset(profile, phsyData)
        offset(profile, phsyData, offset_cmd.distance)


def cancel_offset(profile, phsyData):
    profile.legs = make_leg_from_waypoint(profile.fixedRoute.waypointList)

    curLeg = profile.curLegIdx if profile.offsetInitialLegIdx == -1 else profile.offsetInitialLegIdx
    set_current_leg_idx(profile, curLeg, phsyData)

    profile.offsetRoute = None
    profile.offsetDistance = 0
    profile.offsetInitialLegIdx = -1


def make_leg_from_waypoint(wptLst):
    ret = []
    prePt = None
    for pt in wptLst:
        if prePt:
            ret.append(FlightLeg(prePt, pt))
        prePt = pt
    return ret


def get_third(former, heading, dist):
    heading = (360 + heading) % 360
    later = Waypoint('w', location=Point2D(former.lng, former.lat))
    move_point2d(later.location, heading, dist)

    return later


def offset(profile, phsyData, dist: float):
    if dist == 0:
        return

    refWptLst = profile.fixedRoute.waypointList
    distToTarget = profile.distToTarget
    curIdx = profile.curLegIdx

    heading = phsyData.heading
    first = get_third(phsyData.location, heading, 5 * NM2M)
    delta = dist / abs(dist) * 45
    second = get_third(first.location, heading + delta, abs(dist))

    wpts = refWptLst[:curIdx + 1] + [first, second, ]
    profile.offsetInitialLegIdx = curIdx

    if distToTarget <= 25 * NM2M:
        wpts += refWptLst[curIdx + 2: curIdx + 3]
        profile.offsetInitialLegIdx = curIdx + 1
    elif distToTarget <= 35 * NM2M:
        wpts += refWptLst[curIdx + 1:curIdx + 2]
    else:
        third = get_third(second.location, heading, 18 * NM2M)
        forth = get_third(third.location, heading - delta, abs(dist))
        wpts += [third, forth] + refWptLst[curIdx + 1:curIdx + 2]

    profile.offsetDistance = dist
    profile.offsetRoute = model.Routing(profile.fixedRoute.id, wpts)
    profile.legs = make_leg_from_waypoint(wpts)
    set_current_leg_idx(profile, curIdx, phsyData)


def move_to_next_leg(profile, phsyData):
    set_current_leg_idx(profile, profile.curLegIdx + 1, phsyData)


def set_current_leg_idx(profile, idx: int, phsyData):
    size = len(profile.legs)
    if idx >= size:
        profile.curLegIdx = size
        profile.curLeg = None
        profile.nextLeg = None
        profile.distToTarget = 0
        profile.courseToTarget = 0
        return

    profile.curLegIdx = idx
    profile.curLeg = profile.legs[idx]
    if idx == size - 1:
        profile.nextLeg = None
    else:
        profile.nextLeg = profile.legs[idx + 1]
    update_profile_with_dist_and_course(profile, phsyData)


# 根据下一个点更新到下一个点的距离和航向
def update_profile_with_dist_and_course(profile, phsyData):
    target = profile.target
    if not target:
        profile.distToTarget = 0
        profile.courseToTarget = 0

    profile.distToTarget = phsyData.location.distance_to(target.location)
    profile.courseToTarget = phsyData.location.bearing(target.location)


def update_profile_position(profile, phsyData):
    if not profile.target:
        return
    update_profile_with_dist_and_course(profile, phsyData)
    if target_passed(profile, phsyData):
        move_to_next_leg(profile, phsyData)


# 判断是否通过了此Leg的终点
def target_passed(profile, phsyData, dt: int = 1) -> bool:
    dist = profile.distToTarget
    if dist > 20000:
        return False
    if dist < phsyData.hSpd * dt:
        return True
    if profile.nextLeg:
        turnAngle = (profile.nextLeg.course - profile.curLeg.course) % 360
        prediction = calc_turn_prediction(phsyData.hSpd, turnAngle, phsyData.performance.normTurnRate)
        if dist < prediction:
            return True
    diff = (phsyData.heading - profile.courseToTarget) % 360
    return 270 > diff >= 90


# 计算转弯提前量
def calc_turn_prediction(spd: float, turnAngle: float, turnRate: float) -> float:
    if turnAngle > 180:
        turnAngle = turnAngle - 360
    turnAngle = abs(turnAngle)
    turnRadius = spd / math.radians(turnRate)
    return turnRadius * math.tan(math.radians(turnAngle / 2))  # magic

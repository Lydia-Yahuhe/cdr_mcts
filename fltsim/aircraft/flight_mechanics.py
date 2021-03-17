from __future__ import annotations
from .. import model


def reset_phsydata_with_fpl(pdata, fpl):
    pdata.hSpd = 0
    pdata.vSpd = 0
    pdata.alt = 0
    pdata.heading = 0
    pdata.location.clear()

    pdata.alt = fpl.RFL
    model.compute_performance(pdata.acftType, fpl.RFL, pdata.performance)
    performance = pdata.performance
    pdata.hSpd = performance.normCruiseTAS
    pdata.vSpd = 0
    
    r = fpl.routing
    wpt0 = r.waypointList[0]
    wpt1 = r.waypointList[1]
    pdata.location.set(wpt0.location)
    pdata.heading = wpt0.bearing(wpt1)


def update_phsydata(phsyData, cmd):
    move_horiziontal(phsyData, cmd)
    move_vertical(phsyData, cmd)
    update_performance(phsyData)


def move_horiziontal(pdata, cmd, dt: int = 1):
    performance = pdata.performance
    preHSpd = pdata.hSpd
    if pdata.hSpd > cmd.targetHSpd:
        dec = pdata.acftType.normDeceleration
        pdata.hSpd = max(pdata.hSpd - dec * dt, cmd.targetHSpd)  # /
    elif pdata.hSpd < cmd.targetHSpd:
        acc = pdata.acftType.normAcceleration 
        pdata.hSpd = min(pdata.hSpd + acc * dt, cmd.targetHSpd)  # /
    s = (preHSpd + pdata.hSpd) * dt / 2
    diff = (cmd.targetCourse - pdata.heading) % 360
    if diff > 180:
        diff = diff - 360

    if abs(diff) > 90:
      turn = performance.maxTurnRate * dt
    else: 
      turn = performance.normTurnRate * dt

    if diff < -turn:
      diff = -turn
    elif diff > turn:
      diff = turn

    pdata.heading = (pdata.heading + diff)%360
    pdata.location.move(pdata.heading, s)
    

def move_vertical(pdata, cmd, dt: int = 1):
    diff = cmd.targetAlt - pdata.alt
    
    vS = 0
    if diff < 0:
        vS = max(- pdata.performance.normDescentRate * dt, diff)
    elif diff > 0:
        vS = min(pdata.performance.normClimbRate * dt, diff)
    pdata.alt += vS
    pdata.vSpd = vS / dt       


def update_performance(pdata):
    if pdata.performance.altitude != pdata.alt:
        model.compute_performance(pdata.acftType, pdata.alt, pdata.performance)

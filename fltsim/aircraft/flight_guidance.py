from __future__ import annotations


def reset_flight_guidance(g, fpl):
    g.RFL = fpl.alt
    g.targetAlt = g.RFL
    g.targetHSpd = 0
    g.targetCourse = 0


def update_flight_guidance(now, g, performance, fc, profile):
    if not profile.nextLeg:
        g.RFL = 6000.0

    alt_cmd = fc.altCmd
    if alt_cmd is None:
        g.targetAlt = g.RFL
    elif alt_cmd.assignTime == now:
        g.targetAlt = alt_cmd.targetAlt

    g.targetCourse = profile.courseToTarget
    g.targetHSpd = performance.normCruiseTAS
    spd_cmd = fc.spdCmd
    if spd_cmd and spd_cmd.assignTime == now:
        g.targetHSpd = min(spd_cmd.targetTAS, performance.maxCruiseTAS)
        g.targetHSpd = max(g.targetHSpd, performance.minCruiseTAS)

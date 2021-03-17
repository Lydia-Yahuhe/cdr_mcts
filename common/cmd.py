from fltsim.aircraft import ATCCmdType, atccmd

KT2MPS = 0.514444444444444
NM2M = 1852
flight_level = [i*300.0 for i in range(29)]
flight_level += [i*300.0 + 200.0 for i in range(29, 50)]


def calc_level(target, delta):
    alt, v_spd = target.altitude, target.vspd
    delta = int(delta / 300.0)
    lvl = int(alt / 300.0) * 300.0

    if alt < 8700.0:
        idx = flight_level.index(lvl)
        if (v_spd > 0 and alt - lvl != 0) or (v_spd == 0 and alt - lvl > 150):
            idx += 1

        return flight_level[idx+delta]

    lvl += 200.0
    idx = flight_level.index(lvl)
    if v_spd > 0 and alt - lvl > 0:
        idx += 1
    elif v_spd < 0 and alt - lvl < 0:
        idx -= 1

    return flight_level[idx+delta]


def check_cmd(cmd, a, check):
    if not a.is_enroute or not a.next_leg:
        return False

    # 如果前面出现过调航向，则返回False
    if cmd.cmdType == atccmd.ATCCmdType.LateralOffset:
        if check['hdg'] is not None:
            return False
        else:
            check['hdg'] = 1
            return True

    alt_check, spd_check = check['alt'], check['spd']
    delta = cmd.delta

    # 高度指令限制判断
    if cmd.cmdType == atccmd.ATCCmdType.Altitude:
        # 下降的航空器不能上升，或上升的航空器不能下降
        if a.vspd * delta < 0:
            return False

        RFL, target_alt = a.fpl.alt, cmd.targetAlt

        # 航空器巡航高度±1200m
        if target_alt < RFL - 1800 or target_alt > RFL + 1800:
            return False

        # 最高12000m，最低6000m
        if target_alt > 12000 or target_alt < 6000:
            return False

        # 调过上升，又调下降，或调过下降，又调上升
        if alt_check is None:
            check['alt'] = int(abs(delta)/delta) if delta != 0.0 else 0
        elif alt_check * delta < 0:
            return False
        return True

    # 速度指令限制判断
    if cmd.cmdType == atccmd.ATCCmdType.Speed:
        performance, target_spd = a.performance, cmd.targetTAS
        if performance.maxCruiseTAS < target_spd or target_spd <= performance.minCruiseTAS:
            return False

        # 调过减速，又调减速，或调过减速，又调减速
        if spd_check is None:
            check['spd'] = int(abs(delta) / delta) if delta != 0.0 else 0
        elif spd_check * delta < 0:
            return False

    return True


# 共20个指令【0-15】
def int_2_atc_cmd(time: int, idx: int, target):
    if idx < 0 or idx > 9:
        return None

    if idx < 3:  # [0, 2]  ALT: [-600:600:600]
        delta = (idx - 1) * 600.0
        targetAlt = calc_level(target, delta)
        return atccmd.AltCmd(delta=delta, targetAlt=targetAlt, assignTime=time)

    if idx < 8:  # [3, 7] SPD [-20KT:10KT:20KT]
        delta = (idx - 5) * 10 * KT2MPS
        return atccmd.SpdCmd(delta=delta, targetTAS=target.hspd + delta, assignTime=time)

    if idx == 8:  # 8 HDG 6 NM RIGHT
        return atccmd.LateralOffset(6 * NM2M, assignTime=time)

    if idx == 9:  # 15 HDG 6 NM LEFT
        return atccmd.LateralOffset(-6 * NM2M, assignTime=time)

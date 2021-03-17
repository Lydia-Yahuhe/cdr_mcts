from __future__ import annotations

from copy import deepcopy

from . import atccmd
from .acft_data import AircraftAgentData

from .flight_guidance import update_flight_guidance, reset_flight_guidance
from .flight_mechanics import update_phsydata, reset_phsydata_with_fpl
from .flight_profile import update_profile_position, update_route, reset_flightprofile_with_fpl
from .flightplan_manage import FPLPhase

NM2M = 1852


class AircraftAgent:
    def __init__(self, fpl, time=0):
        self.id = fpl.id
        aircraft = self.aircraft = fpl.aircraft
        self.fpl = fpl
        self.phase = FPLPhase.Schedule
        self.data = AircraftAgentData(aircraft.id, aircraft.aircraftType, time)
        self.tracks = {}

    def aircraft_type(self):
        return self.data.phsyData.acftType

    @property
    def is_enroute(self):
        return self.phase == FPLPhase.EnRoute
    
    @property
    def performance(self):
        return self.data.phsyData.performance
    
    @property
    def location(self):
        return self.data.phsyData.location
    
    @property
    def hspd(self):
        return self.data.phsyData.hSpd
    
    @property
    def vspd(self):
        return self.data.phsyData.vSpd

    @property
    def heading(self):
        return self.phsy_data.heading
    
    @property
    def phsy_data(self):
        return self.data.phsyData

    @property
    def next_leg(self):
        return self.data.profile.nextLeg

    @property
    def next_four(self):
        return self.data.profile.next_four

    @property
    def altitude(self):
        return self.data.phsyData.alt

    @property
    def position(self):
        loc = self.location
        return [loc.lng, loc.lat, self.altitude]

    def x_data(self):
        phsyData = self.data.phsyData
        return self.position + [phsyData.hSpd, phsyData.vSpd, phsyData.course]

    def do_step(self, dt=1):
        if self.phase == FPLPhase.Finished:
            return

        data = self.data
        profile, fltCtr, phsyData, fltCmd = data.profile, data.fltCtr, data.phsyData, data.fltCmd
        for _ in range(dt):
            now = data.add_time()

            if self.is_enroute:
                update_route(profile, phsyData, fltCtr, now)
                update_flight_guidance(now, fltCmd, phsyData.performance, fltCtr, profile)
                update_phsydata(phsyData, fltCmd)
                update_profile_position(profile, phsyData)

                self.tracks[now] = self.position + [phsyData.hSpd, phsyData.vSpd, phsyData.course]

                if not profile.target:
                    self.phase = FPLPhase.Finished
                    return
                continue

            fpl = self.fpl
            if fpl.startTime == now:
                reset_flight_guidance(data.fltCmd, fpl)
                reset_phsydata_with_fpl(data.phsyData, fpl)
                reset_flightprofile_with_fpl(data.profile, fpl)
                self.phase = FPLPhase.EnRoute

    def assign_cmd(self, cmd):
        if cmd.cmdType == atccmd.ATCCmdType.Altitude:
            self.data.fltCtr.altCmd = cmd
        elif cmd.cmdType == atccmd.ATCCmdType.Speed:
            self.data.fltCtr.spdCmd = cmd
        elif cmd.cmdType == atccmd.ATCCmdType.LateralOffset:
            self.data.fltCtr.offsetCmd = cmd

    def reset(self, other):
        self.id = other.id
        self.aircraft = other.fpl.aircraft
        self.fpl = other.fpl
        self.phase = other.phase
        self.data = deepcopy(other.data)
        self.tracks = deepcopy(other.tracks)


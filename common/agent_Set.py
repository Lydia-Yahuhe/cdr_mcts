from __future__ import annotations

from fltsim import save_to_kml
from fltsim.geom import make_bbox, build_rt_index, distance
from .util import make_agent_set, copy_agent_set, Conflict


class AircraftAgentSet:
    def __init__(self, fpl_list=None, supply=None, other=None):
        self.ac_en, self.ac_en_ = [], []

        if fpl_list:
            self.agents, self.time = make_agent_set(fpl_list, supply[1])
            self.tracks = supply[0]
            self.check_list = []
        else:
            self.agents, self.time = copy_agent_set(other)
            self.tracks = other.tracks
            self.check_list = other.check_list[:]

    def do_step(self, duration=1, basic=False):
        self.ac_en, now = [], self.time

        duration -= now * int(basic)
        for key, agent in self.agents.items():
            agent.do_step(duration)

            if agent.is_enroute:
                self.ac_en.append([key] + agent.x_data())

        now += duration

        ac_en_ = []
        for key, track in self.tracks.items():
            if now in track.keys():
                ac_en_.append(track[now])

        self.ac_en_ = self.ac_en + ac_en_
        self.time = now

    def detect_conflict_list(self, search=None):
        if len(self.ac_en) <= 0:
            return []

        conflicts, ac_en = [], self.ac_en_
        idx = build_rt_index(ac_en)
        for [a0, *pos0] in self.ac_en:
            if a0 not in search:
                continue

            bbox = make_bbox(pos0, (0.1, 0.1, 299))

            for i in idx.intersection(bbox):
                [a1, *pos1] = ac_en[i]
                if a0 == a1 or a0 + "-" + a1 in self.check_list:
                    continue

                conflict = self.detect_conflict(a0, a1, pos0, pos1)
                if conflict:
                    conflicts.append(conflict)
        return conflicts

    def detect_conflict(self, a0, a1, pos0, pos1):
        h_dist = distance(pos0, pos1)
        v_dist = abs(pos0[2] - pos1[2])

        if h_dist >= 10000 or v_dist >= 300.0:
            return None

        c_id = [a0+"-"+a1, a1+"-"+a0]
        self.check_list += c_id

        return Conflict(id=c_id[0], time=self.time, hDist=h_dist, vDist=v_dist, pos0=pos0, pos1=pos1)

    def visual(self, save_path='agentSet'):
        tracks = {}
        for a_id, agent in self.agents.items():
            tracks[a_id] = [track[:3] for track in agent.tracks.values()]

        save_to_kml(tracks, save_path=save_path)


from common import AircraftAgentSet, int_2_atc_cmd, check_cmd
from common.util import read_from_csv
from fltsim import equal


class ConflictScene:
    def __init__(self, info, root='train'):
        self.conflict_ac, self.clock = info['conflict_ac'], info['time']
        self.agentSet = AircraftAgentSet(fpl_list=info['fpl_list'],
                                         supply=read_from_csv(info['id'], self.conflict_ac, root))

        self.cmd_list = {'alt': None, 'spd': None, 'hdg': None}
        self.record = {}
        self.c_ac = None

    @property
    def now(self):
        return self.agentSet.time

    def prepare(self):
        conflicts = []
        traj_dict = {}
        ghost = AircraftAgentSet(other=self.agentSet)
        while ghost.time <= self.clock+300:
            ghost.do_step()
            conflicts += ghost.detect_conflict_list(search=self.conflict_ac)

            for a_id, agent in ghost.agents.items():
                now = ghost.time
                if not agent.is_enroute and now % 8 == 0:
                    continue

                if a_id not in traj_dict.keys():
                    traj_dict[a_id] = {now: agent.position}
                else:
                    traj_dict[a_id][now] = agent.position

        if len(conflicts) <= 0:
            print('conflicts length is zero!')
            return False

        tmp_time, tmp_ac = [], []
        for c in conflicts:
            tmp_time.append(c.time)
            tmp_ac += c.id.split('-')

        print(self.clock, tmp_time, tmp_ac, self.conflict_ac, end='\t')

        if not (equal(list(set(tmp_ac)), self.conflict_ac) or max(tmp_time) - min(tmp_time) <= 300):
            print('not equal or time not match!')
            return False

        tmp = []
        while len(tmp_ac) > 0:
            ac = tmp_ac.pop(0)
            if ac in tmp_ac:
                tmp.append(ac)
        tmp = list(set(tmp))
        print(tmp)
        if len(tmp) != 1:
            return False
        self.c_ac = tmp[0]
        self.clock = min(tmp_time)
        self.agentSet.do_step(self.clock - 270, basic=True)
        self.record['former'] = traj_dict[tmp[0]]
        return True

    def execute_and_detect(self, action):
        """
        将字符串转换成对应的命令，并分配给航空器
        """
        cmd = {int(action[:3])+self.clock-270: int(action[3:])}
        solve, ok = self.ghost_run(cmd)
        return solve, ok

    def get_agent_with_id(self, agent_id, agents=None):
        if agents is None:
            agents = self.agentSet.agents
        return agents[agent_id]

    def ghost_run(self, cmd_dict=None):
        clock = self.clock
        traj_dict = {}
        ok_total = 0

        ghost = AircraftAgentSet(other=self.agentSet)
        end_time = clock+360

        while ghost.time < end_time:
            ghost.do_step()
            conflicts = ghost.detect_conflict_list(search=[self.c_ac])
            if len(conflicts) > 0:
                return False, ok_total

            agent = ghost.agents[self.c_ac]
            now = ghost.time
            if agent.is_enroute and now % 8 == 0:
                traj_dict[now] = agent.position

            if cmd_dict is not None and now+1 in cmd_dict.keys():
                idx = cmd_dict[now+1]
                cmd = int_2_atc_cmd(now+1, idx, agent)
                ok_total = int(check_cmd(cmd, agent))
                if ok_total > 0:
                    agent.assign_cmd(cmd)
                    # print(self.agentSet.time, idx, now, cmd, agent.data.fltCtr)

        self.record['later'] = traj_dict
        return True, ok_total


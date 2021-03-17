
from common import AircraftAgentSet, int_2_atc_cmd, check_cmd
from common.util import read_from_csv
from fltsim import equal

CmdCount = 10


class ConflictScene:
    def __init__(self, info, root='train'):
        self.conflict_ac, self.clock = info['conflict_ac'], info['time']

        self.agentSet = AircraftAgentSet(fpl_list=info['fpl_list'],
                                         supply=read_from_csv(info['id'], self.conflict_ac, root))

        self.cmd_list = {'alt': None, 'spd': None, 'hdg': None}
        self.c_ac = None

    @property
    def now(self):
        return self.agentSet.time

    def prepare(self):
        conflicts = []
        ghost = AircraftAgentSet(other=self.agentSet)
        while ghost.time <= self.clock+300:
            ghost.do_step()
            conflicts += ghost.detect_conflict_list(search=self.conflict_ac)

        if len(conflicts) <= 0:
            print('conflicts length is zero!')
            return False

        tmp_time, tmp_ac = [], []
        for c in conflicts:
            tmp_time.append(c.time)
            tmp_ac += c.id.split('-')

        print(tmp_time, tmp_ac, self.conflict_ac, end='\t')

        if not (equal(list(set(tmp_ac)), self.conflict_ac) or max(tmp_time) - min(tmp_time) <= 300):
            print('not equal or time not match!')
            return False

        tmp = []
        while len(tmp_ac) > 0:
            ac = tmp_ac.pop(0)
            if ac in tmp_ac:
                tmp.append(ac)
        tmp = list(set(tmp))
        if len(tmp) != 1:
            return False
        self.c_ac = tmp[0]
        self.clock = min(tmp_time)
        self.agentSet.do_step(self.clock - 270, basic=True)
        print(self.clock, tmp)
        return True

    def takeAction(self, action, agentSet, check):
        """
        将字符串转换成对应的命令，并分配给航空器
        """
        # 复制
        ghost = AircraftAgentSet(other=agentSet)
        assign_time = ghost.time

        # 解析命令
        target = ghost.agents[self.c_ac]
        if action >= CmdCount:
            return None
        cmd = int_2_atc_cmd(assign_time+1, action, target)
        ok = check_cmd(cmd, target, check)

        # 分配命令
        if ok and target.is_enroute:
            target.assign_cmd(cmd)

        # 执行命令
        conflicts = []
        while ghost.time < assign_time + 120:
            ghost.do_step(duration=30)
            conflicts += ghost.detect_conflict_list(search=[self.c_ac])

        return ghost, len(conflicts) > 0, ghost.time < self.clock, ok


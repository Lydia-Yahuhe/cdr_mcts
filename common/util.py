from dataclasses import dataclass

from rtree import index

from fltsim import load_data_set, make_bbox_2d
from fltsim.aircraft import AircraftAgent

data_set = load_data_set()
wpt_dict = data_set.waypoints
wpt_list = list(wpt_dict.values())
wpt_size = len(wpt_list)

rou_dict = {}
for key, route in data_set.routings.items():
    lst = []
    for wpt in route.waypointList:
        wpt = wpt.location
        lst.append([wpt.lng, wpt.lat])
    rou_dict[key] = lst


def rt_index():
    p = index.Property()
    p.dimension = 2
    idx = index.Index(properties=p)
    for i, wpt in enumerate(wpt_list):
        loc = wpt.location
        idx.insert(i+1, make_bbox_2d((loc.lng, loc.lat)))
    return idx


idx = rt_index()


# 获得bbox范围内的航路点代号
def get_points_in_bbox(bbox):
    lst_ = []
    tmp = list(bbox[:2]) + list(bbox[3:5])
    for i in idx.intersection(tmp):
        wpt = wpt_list[i-1].location
        lst_ += [(wpt.lng-110)/30, (wpt.lat-35)/15]

    lst_ += [0.0 for _ in range(100)]
    return lst_[:100]


def read_from_csv(file_name, limit, root):
    if file_name is None:
        return [{}, None]

    # import time
    # start = time.time()
    # file_name = 'E:\\Workspace\\{}_data\\{}.csv'.format(root, file_name)
    # with open(file_name, 'r', newline='') as f:
    #     ret = {}
    #     for line in f.readlines():
    #         [fpl_id, time_, *line] = line.strip('\r\n').split(',')
    #         if fpl_id in limit:
    #             continue
    #
    #         if fpl_id in ret.keys():
    #             ret[fpl_id][int(time_)] = [fpl_id] + [float(x) for x in line]
    #         else:
    #             ret[fpl_id] = {int(time_): [fpl_id] + [float(x) for x in line]}
    #     time_list.append(time.time()-start)
    #     print(sum(time_list)/len(time_list))
    #     return [ret, limit]

    file_name = 'E:\\Workspace\\{}_data_8\\{}.csv'.format(root, file_name)
    with open(file_name, 'r', newline='') as f:
        ret = {}
        for line in f.readlines():
            line = line.replace('\"', '')
            [fpl_id, time_, *line] = line.strip('\r\n').split(',')
            if fpl_id in limit:
                continue

            if fpl_id in ret.keys():
                time_ = int(time_)
                last_one = ret[fpl_id][time_-8][1:]
                this_one = [float(x) for x in line]
                for i in range(8):
                    ret[fpl_id][time_-7+i] = [fpl_id] + [(i+1)*(this_one[j]-x)/8 for j, x in enumerate(last_one)]
            else:
                ret[fpl_id] = {int(time_): [fpl_id] + [float(x) for x in line]}
        return [ret, limit]


def copy_agent_set(other):
    agents = {}
    for aid, agent in other.agents.items():
        ret = AircraftAgent(agent.fpl)
        ret.reset(agent)
        agents[aid] = ret

    return agents, other.time


def make_agent_set(fpl_list, supply=None):
    agents = {}
    for fpl in fpl_list:
        fpl_id = fpl.id
        if supply and fpl_id not in supply:
            continue

        agents[fpl_id] = AircraftAgent(fpl)

    return agents, 0


@dataclass
class Conflict:
    id: str
    time: int
    hDist: float
    vDist: float
    pos0: tuple
    pos1: tuple

    def tostring(self):
        print(self.id, self.time, self.hDist, self.vDist, self.pos0, self.pos1)

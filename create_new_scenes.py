import random
import pymongo

from common import AircraftAgentSet
from fltsim import load_data_set

data_set = load_data_set()
flight_plan = list(data_set.flightPlans.values())
fpl_idx = list(range(len(flight_plan)))

connection = pymongo.MongoClient('localhost')
collection = connection['admin']['scenes_mcts']


def get_fpl_list(size):
    random.shuffle(fpl_idx)

    fpl_list = []
    for idx in fpl_idx[:size]:
        fpl = flight_plan[idx]
        fpl.startTime = random.randint(0, 3600)
        fpl_list.append(fpl)
    return fpl_list


def is_two_conflict(conflicts):
    size = len(conflicts)
    if size == 1:
        return True, conflicts[0]

    if size == 0:
        return False, -1

    [first, second] = conflicts[:2]
    ok = second.time-first.time >= 360
    return ok, conflicts[0]


def make_scene():
    count = 3000
    size = 80

    while count > 0:
        print('---------No.{}------------'.format(count))
        fpl_list = get_fpl_list(size)
        agent_set = AircraftAgentSet(fpl_list=fpl_list)

        conflicts = []
        while not agent_set.done:
            agent_set.do_step()
            conflicts += agent_set.detect_conflict_list()

        print('conflicts:', agent_set.time, len(conflicts))
        for conflict in conflicts:
            conflict.dump()

        ok, conflict = is_two_conflict(conflicts)
        if not ok:
            continue

        fpl_info = []
        for fpl in fpl_list:
            fpl_info.append(
                dict(id=fpl.id,
                     ac=fpl.aircraft.id,
                     ac_type=fpl.aircraft.aircraftType.id,
                     alt=fpl.alt,
                     RFL=fpl.RFL,
                     start=fpl.startTime,
                     routing=fpl.routing.id))

        scene_info = dict(id='No.{}'.format(count),
                          conflict_ac=conflict.id.split('-'),
                          clock=conflict.time,
                          fpl_list=fpl_info)
        collection.insert(scene_info)
        count -= 1


# MCTS对比算法GA，双机冲突，80架航空器，随机生成场景
if __name__ == '__main__':
    make_scene()

from mcts import mcts

from common import AircraftAgentSet, int_2_atc_cmd, check_cmd
from fltmcts.scene_mcts import ConflictScene
from fltsim import load_train_data, save_to_kml

if __name__ == "__main__":
    searcher = mcts(iterationLimit=1000)
    scenes = load_train_data()

    for i, info in enumerate(scenes):
        # 输出场景信息：编号，航空器对的id，场景航空器架次，冲突时间
        print('\n正在测试第{}个场景......'.format(i + 1))

        scene = ConflictScene(info)
        # if not scene.prepare():
        #     continue
        clock, agent_set, conflict_ac = scene.clock, scene.agentSet, scene.conflict_ac
        conflicts_g = []
        ghost = AircraftAgentSet(other=scene.agentSet)
        while ghost.time <= clock + 300:
            ghost.do_step()
            conflicts_g += ghost.detect_conflict_list(search=conflict_ac)

        # ghost.visual(save_path='ghost')

        agent_set.do_step(clock - 270, basic=True)
        cmd_dict = {(conflict_ac[2], clock - 180): 9, (conflict_ac[2], clock - 120): 8}
        # cmd_dict = {(conflict_ac[2], clock - 190): 2}

        conflicts_a = []
        while agent_set.time < clock + 300:
            agent_set.do_step()
            conflicts_a += agent_set.detect_conflict_list(search=conflict_ac)

            now = agent_set.time
            for a_id, agent in agent_set.agents.items():
                key = (a_id, now+1)
                if cmd_dict is not None and key in cmd_dict.keys():
                    idx = cmd_dict[key]
                    cmd = int_2_atc_cmd(now+1, idx, agent)
                    ok_total = int(check_cmd(cmd, agent))
                    print(clock - 270, now+1, idx, ok_total, cmd, agent.id)
                    if ok_total > 0:
                        agent.assign_cmd(cmd)
                        print(agent.data.fltCtr)

        print(len(conflicts_g), len(conflicts_a))
        for conflict_g, conflict_a in zip(conflicts_g, conflicts_a):
            conflict_g.tostring()
            conflict_a.tostring()

        agent_set.visual('agent_set')
        break


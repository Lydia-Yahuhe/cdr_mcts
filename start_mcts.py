import csv

from mcts import mcts

from fltmcts.scene_mcts import ConflictScene
from fltsim import load_train_data


if __name__ == "__main__":
    import time

    searcher = mcts(iterationLimit=1000)
    scenes = load_train_data()

    for i, info in enumerate(scenes):
        # 输出场景信息：编号，航空器对的id，场景航空器架次，冲突时间
        print('\n正在测试第{}个场景......'.format(i+1))

        scene = ConflictScene(info)
        if not scene.prepare():
            continue

        start = time.time()
        result = searcher.search(initialState=scene)
        delta = time.time()-start
        result.append(delta)
        print(result)

        with open('record_mcts.csv', 'a+', newline='') as f:
            f = csv.writer(f)
            f.writerow(result)

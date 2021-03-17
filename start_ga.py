import csv

from fltga import ConflictScene, GA
from fltsim import load_train_data


def main():
    scenes = load_train_data()

    for i, info in enumerate(scenes):
        # 输出场景信息：编号，航空器对的id，场景航空器架次，冲突时间
        print('\n正在测试第{}个场景......'.format(i+1))

        scene = ConflictScene(info)
        if not scene.prepare():
            continue

        # 利用遗传算法求解
        ga = GA(scene)
        result = ga.GA_main()
        with open('record_ga.csv', 'a+', newline='') as f:
            f = csv.writer(f)
            f.writerow([i, len(info['fpl_list'])]+result)
        print(result)


if __name__ == '__main__':
    main()

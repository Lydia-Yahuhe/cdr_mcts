import math
import time
import random
from operator import itemgetter

from fltsim import save_to_kml


class Gene:
    """
    This is a class to represent individual(Gene) in GA algorithm
    each object of this class have two attribute: data, size
    """

    def __init__(self, **data):
        self.__dict__.update(data)
        self.size = len(data['data'])  # length of gene


class GA:
    """
    This is a class of GA algorithm.
    """
    def __init__(self, scene, cxpb=0.6, mutpb=0.5, ngen=100, popsize=10):
        """
        Initialize the pop of GA algorithm and evaluate the pop by computing its' fitness value.
        The data structure of pop is composed of several individuals which has the form like that:

        {'Gene':a object of class Gene, 'fitness': 1.02(for example)}
        Representation of Gene is a list: [b s0 u0 sita0 s1 u1 sita1 s2 u2 sita2]

        """
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.ngen = ngen
        self.popsize = popsize
        self.scene = scene

        pop = []
        for i in range(self.popsize):
            time_ = str(random.randint(0, 270)).zfill(3)
            idx_ = str(random.randint(0, 10)).zfill(2)
            geneinfo = time_+idx_

            pop.append({'Gene': Gene(data=geneinfo), 'fitness': self.evaluate(geneinfo)})

        self.pop = pop
        self.bestindividual = self.selectBest(self.pop)

    def evaluate(self, action):
        """
        fitness function（传入的是指令表示的解脱航迹）
        """
        solved, ok = self.scene.execute_and_detect(action)
        # print(action, solved, ok)

        if not solved:
            # print('Failed!!!', ok, fitness_1, '\n')
            return 0.0

        record = self.scene.record
        former = record['former']
        sum_dist = 0.0
        points_former, points_later = [], []
        for key, point_a in record['later'].items():
            if key not in former.keys():
                continue

            point_b = former[key]
            points_former.append(point_b)
            points_later.append(point_a)
            lon_dist = abs(point_a[0] - point_b[0]) / 10000.0
            lat_dist = abs(point_a[1] - point_b[1]) / 10000.0
            ver_dist = abs(point_a[2] - point_b[2]) / 300.0
            sum_dist += math.sqrt(lon_dist ** 2 + lat_dist ** 2 + ver_dist ** 2)

        # save_to_kml({'former': points_former, 'latter': points_later})
        # fitness_1: 指令正确与否
        fitness_1 = ok - 1

        # fitness_2: 原航路偏差
        fitness_2 = math.exp(sum_dist/-100)

        # fitness
        fitness = fitness_1 + fitness_2
        # print('Solved!!!', sum_dist, fitness_1, fitness_2, fitness, '\n')
        return fitness

    def selectBest(self, pop):
        """
        select the best individual from pop
        """
        return sorted(pop, key=itemgetter("fitness"), reverse=True)[0]

    def selection(self, individuals, k):
        """
        select some good individuals from pop, note that good individuals have greater
        probability to be chosen, for example: a fitness list like that:[5, 4, 3, 2, 1],
        sum is 15:
            [-----|----|---|--|-]
            012345|6789|101112|1314|15
        we randomly choose a value in [0, 15], it belongs to first scale with greatest
        probability.
        """
        s_inds = sorted(individuals, key=itemgetter("fitness"), reverse=True)
        sum_fits = sum(ind['fitness'] for ind in individuals)

        chosen = []
        for i in range(k):
            u = random.random() * sum_fits  # randomly produce a num in [0, sum_fits] as threshold
            sum_ = 0
            for ind in s_inds:
                sum_ += ind['fitness']  # sum up the fitness
                if sum_ >= u:
                    # when the sum of fitness is bigger than u, choose the one, which means u
                    # is in [sum(1,2,...,n-1), sum(1,2,...,n)] and is time to choose the one,
                    # namely n-th individual in the pop.
                    chosen.append(ind)
                    break

        # from small to large, due to list.pop() method get the last element
        chosen = sorted(chosen, key=itemgetter("fitness"), reverse=False)
        return chosen

    def crossoperate(self, offspring):
        """
        cross operation
        here we use two points cross operate, for example:

        gene1: [5, 2, 4, 7], gene2: [3, 6, 9, 2],
        if pos1=1, pos2=2:
            5 | 2 | 4  7     5 | 6 | 4  7
            3 | 6 | 9  2  =  3 | 2 | 9  2
        """
        [geninfo1, geninfo2] = [list(osp_['Gene'].data) for osp_ in offspring]

        # select a position in the range from 0 to dim-1
        g1_time, g1_action = geninfo1[:3], geninfo1[3:]
        g2_time, g2_action = geninfo2[:3], geninfo2[3:]

        if random.randint(0, 100) % 2 == 0:
            return Gene(data=''.join(g1_time+g2_action)), Gene(data=''.join(g2_time+g1_action))
        return Gene(data=''.join(g2_time+g1_action)), Gene(data=''.join(g1_time+g2_action))

    def mutation(self, crossoff):
        """
        mutation operation
        """
        time_ = str(random.randint(0, 270)).zfill(3)
        idx_ = str(random.randint(0, 10)).zfill(2)
        crossoff.data = time_ + idx_
        return crossoff

    def GA_main(self):
        start = time.time()
        g, counter = 0, 0

        # print("------ Start of evolution ------")
        for g in range(self.ngen):
            print("\t\t>>> Generation {}".format(g), end='\t')

            # Apply selection based on their converted fitness
            selectpop = self.selection(self.pop, self.popsize)

            nextoff = []
            while len(nextoff) != self.popsize:
                # Select two individuals
                offspring = [selectpop.pop(), selectpop.pop()]

                # cross two individuals with probability CXPB
                if random.random() < self.cxpb:
                    crossoff1, crossoff2 = self.crossoperate(offspring)

                    # mutate an individual with probability MUTPB
                    if random.random() < self.mutpb:
                        crossoff1 = self.mutation(crossoff1)
                    if random.random() < self.mutpb:
                        crossoff2 = self.mutation(crossoff2)

                    # Evaluate the individuals
                    fit_crossoff1 = self.evaluate(crossoff1.data)
                    fit_crossoff2 = self.evaluate(crossoff2.data)

                    nextoff.append({'Gene': crossoff1, 'fitness': fit_crossoff1})
                    nextoff.append({'Gene': crossoff2, 'fitness': fit_crossoff2})
                else:
                    nextoff.extend(offspring)

            # The population is entirely replaced by the offspring
            self.pop = nextoff

            # Gather all the fitness in one list and print the stats
            fits = [ind['fitness'] for ind in self.pop]
            best_ind = self.selectBest(self.pop)

            if best_ind['fitness'] > self.bestindividual['fitness']:
                self.bestindividual = best_ind
                counter = 0
            else:
                counter += 1

            print(self.bestindividual['Gene'].data, self.bestindividual['fitness'], max(fits))

            if counter >= 15:
                break

        # print("------ End of (successful) evolution ------")
        end = time.time()
        data = self.bestindividual['Gene'].data

        return [g, end-start, data, self.bestindividual['fitness']]


import enum
import math
import random

import numpy
from openpyxl import load_workbook

# %%
# Annex1：node＆link.xlsx
wb = load_workbook('1.xlsx')
sheets = wb.worksheets
sheet_point_list = sheets[0]
sheet_distance = sheets[1]
# 求解的目标阵营
targetCamp = 'blue'

# %%
# id->point哈希表
pointMap = {}
for row in tuple(sheet_point_list.values)[1:]:
    id_ = int(row[0])
    x = float(row[1])
    y = float(row[2])
    camp = row[3]
    attackDifficulty = float(row[4])
    pointMap[id_] = {
        x: x,
        y: y,
        camp: camp,
        attackDifficulty: attackDifficulty
    }

# 红方剔除孤立点剔除
exceptList = '159 1 24 4 23 18 5 17 20 12 19 16 13 21 22 15 11 8 10 9 6 14 7'.split()
exceptList = []
exceptList = numpy.array(exceptList, dtype=int)
pointList = []
for row in list(sheet_point_list.values)[1:]:
    if row[0] in exceptList:
        continue
    pointList.append(row)

# 先在距离表中剔除敌方点
pointList = numpy.array(pointList)
# 敌方id列表
enemyIdList = numpy.array(pointList[pointList[:, -2] != targetCamp][:, 0], dtype=int)
# 己方id列表
myIdList = numpy.array(pointList[pointList[:, -2] == targetCamp][:, 0], dtype=int)
# 己方据点个数
myArmPointSize = len(myIdList.tolist())
import data.t1_1_data as t1_1_data

blueCampDistanceMatrix = t1_1_data.blueCampDistanceMatrix
blueCampAdjacencyMatrix = t1_1_data.blueCampAdjacencyMatrix


class Arms(enum.Enum):
    # 一万步兵
    infantry = 1
    lightTank = 2
    mediumTank = 3
    heavyTank = 4
    # 自行火炮
    selfPropelledGun = 5
    # 无人机
    UAV = 6


# 火力映射表
fireMap = {
    Arms.infantry: 4.44,
    Arms.lightTank: 1.01,
    Arms.mediumTank: 1.14,
    Arms.heavyTank: 1.92,
    Arms.selfPropelledGun: 0.047,
}

"""
计算所有点的安全系数
armSizeList 各点兵力数量
arms 各点兵种分布
"""


def getSafeRatio(armSizeList, arms):
    # 距离平衡系数
    K2 = 1
    totalSafeRatio = []
    # 当前计算点，设A点
    for currentCalcIndex, currentCalcPoint, in enumerate(myIdList):
        currentSafeRatio = 0
        # 求和其他点，设B,C点
        for index, point in enumerate(myIdList):
            if index == currentCalcIndex:
                continue
            # 火力
            fireParam = fireMap[Arms[arms[index]]]
            # 兵力数量
            weaponSizeParam = armSizeList[index]
            # B,C点和其他点是否连通
            isConnected = 1 if blueCampAdjacencyMatrix[index].tolist().count(numpy.inf) == 0 else 0
            # B,C点离所有其他点的距离之和
            distanceParam = blueCampDistanceMatrix.sum(axis=0)[index]
            currentSafeRatio += fireParam * weaponSizeParam * isConnected / (K2 * distanceParam)

        totalSafeRatio.append(currentSafeRatio)

    return totalSafeRatio


def getDangerRatio(armSizeList, arms):
    pass


# %%
# 遗传

class GA:
    """
    population_size 种群数量
    x 参数个数
    iterations 迭代次数
    Mutates_rate 突变率
    select_rate 选择率
    """

    def __init__(self, population_size, x, iterations, Mutates_rate, select_rate, lb, ub):
        self.population_size = population_size
        self.population = []
        self.x = x
        self.iterations = iterations
        self.Mutates_rate = Mutates_rate
        self.select_rate = select_rate
        self.decode_dic = {}
        self.lb = lb
        self.ub = ub
        self.count_Dight()

    # 计算编码长度
    def count_Dight(self):
        self.Dight = []
        for i in range(len(self.ub)):
            dight = math.ceil(math.log(self.ub[i], 2))
            self.Dight.append(dight)

    # 解码
    def Decode(self, Genes):
        res = 0
        for i in Genes:
            res = res * 2 + i
        return res

    # 编码
    def Coding(self, data, x):
        l = []
        while data != 0:
            l.append(data % 2)
            data //= 2
        for i in range(x - len(l)):
            l.append(0)
        return l[::-1]

    # 适应度函数
    def count_suit(self, Individuals):
        decodedList = []
        for Genes in Individuals:
            if self.decode_dic.get(tuple(Genes), -1) == -1:
                data = self.Decode(Genes)
                self.decode_dic[tuple(Genes)] = data
            else:
                data = self.decode_dic[tuple(Genes)]
            decodedList.append(data)
        # ori = 32
        score = 0
        for pointId in decodedList:
            score += pointMap[pointId]['attackDifficulty']
        # for i in decodedList:
        #     if ori != i:
        #         score += message[ori][i]
        #         ori = i
        # score += message[ori][32]
        return score

    # 初始种群
    def init_population(self):
        progress = 1000
        for i in range(self.population_size):
            # 一个个体 或者说是一个方案
            chromosome = {
                # 兵种数量
                'armSize': [random.randint(1, 100 + 1) for _ in range(myArmPointSize)],
                # 各个节点的兵种
                'arm': [random.randint(1, 5 + 1) for _ in range(myArmPointSize)]
            }

            t = []
            for i in range(len(chromosomeArmSize)):
                t.append(self.Coding(chromosomeArmSize[i], self.Dight[i]))
            res = self.count_suit(t)
            for h in range(progress):
                new = []
                for i in t:
                    new.append(i.copy())
                while True:
                    x1 = numpy.random.randint(0, self.x)
                    x2 = numpy.random.randint(0, self.x)
                    if x1 != x2:
                        break
                p = new[x1]
                new[x1] = new[x2]
                new[x2] = p
                if self.count_suit(new) < res:
                    t = []
                    for j in new:
                        t.append(j.copy())
            self.population.append(t)

    # 种群适应度计算
    def Fitness(self):
        save = []
        the_sum = 0
        for Individuals in self.population:
            res = self.count_suit(Individuals)
            the_sum += res
            save.append([Individuals.copy(), res])
        self.population_size = len(save)
        return save, the_sum

    # 选择
    def Select(self):
        save, the_sum = self.Fitness()
        grad = [x[0] for x in sorted(save, key=lambda x: x[1])]
        length = 300
        new_population = grad[:length]
        f = math.floor(math.log(self.population_size, 2))
        for i in grad[length:]:
            if random.random() < self.select_rate and f > 0:
                new_population.append(i)
                f -= 1
        self.population = new_population
        self.population_size = len(new_population)

    # 交叉
    def Crisscross(self):
        for i in range(self.population_size):
            while True:
                x1 = numpy.random.randint(0, self.population_size)
                x2 = numpy.random.randint(0, self.population_size)
                if x1 != x2:
                    break
            left = numpy.random.randint(0, int(self.x / 2) + 1)
            right = numpy.random.randint(left + 1, self.x)
            new_child1 = []
            new_child2 = []
            parents1 = []
            parents2 = []
            for j in self.population[x1][left:right + 1]:
                parents1.append(j.copy())
            for j in self.population[x2][left:right + 1]:
                parents2.append(j.copy())
            dot = random.randint(0, self.x - len(parents1))
            for j in self.population[x1]:
                if j not in parents2:
                    new_child1.append(j.copy())
            for j in self.population[x2]:
                if j not in parents1:
                    new_child2.append(j.copy())
            new_child1 = new_child1[0:dot] + parents2 + new_child1[dot:]
            new_child2 = new_child2[0:dot] + parents1 + new_child2[dot:]
            # print('len',len(new_child1))
            self.population.append(new_child1)
            self.population.append(new_child2)
        self.population_size = len(self.population)

    # 变异
    def Mutates(self):
        for i in range(self.population_size):
            if random.random() < self.Mutates_rate:
                x = numpy.random.randint(0, self.population_size)
                while True:
                    dot1 = numpy.random.randint(0, self.x)
                    dot2 = numpy.random.randint(0, self.x)
                    if dot1 != dot2:
                        break
                new = []
                for j in self.population[x]:
                    new.append(j.copy())
                t = new[dot1]
                new[dot1] = new[dot2]
                new[dot2] = t
                self.population.append(new)
        self.population_size = len(self.population)

    def run_it(self):
        self.init_population()
        print(self.population)
        for i in range(self.iterations):
            self.Select()
            self.Crisscross()
            self.Mutates()
            if i % 10 == 0:
                print(self.population_size)
                print("finish", i + 1)
        self.the_res = 100000
        self.way = "##"
        t = self.Fitness()
        print(len(t[0]))
        for i in range(len(t[0])):
            if i % 10 == 0:
                print(t[0][i][1])
            if self.the_res > t[0][i][1]:
                self.the_res = t[0][i][1]
                self.way = t[0][i][0]
        res_dic = {}
        for i in self.way:
            data = self.Decode(i)
            if res_dic.get(data, -1) == -1:
                res_dic[data] = 1
            else:
                res_dic[data] += 1
        print(res_dic)


ga = GA(100, 31, 1000, 0.3, 0.5, numpy.ones(31), 31 * numpy.ones(31))
ga.run_it()

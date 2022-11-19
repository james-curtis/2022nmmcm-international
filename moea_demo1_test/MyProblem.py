# -*- coding: utf-8 -*-
"""Demo.

min f1 = -25 * (x1 - 2)**2 - (x2 - 2)**2 - (x3 - 1)**2 - (x4 - 4)**2 - (x5 - 1)**2
min f2 = (x1 - 1)**2 + (x2 - 1)**2 + (x3 - 1)**2 + (x4 - 1)**2 + (x5 - 1)**2
s.t.
x1 + x2 >= 2
x1 + x2 <= 6
x1 - x2 >= -2
x1 - 3*x2 <= 2
4 - (x3 - 3)**2 - x4 >= 0
(x5 - 3)**2 + x4 - 4 >= 0
x1,x2,x3,x4,x5 ∈ {0,1,2,3,4,5,6,7,8,9,10}
"""
import enum
import math
import pickle
import time
import numba
import numpy as np
from openpyxl import load_workbook
import geatpy as ea
import data.t1_1_data as data
from multiprocessing import Pool as ProcessPool
import multiprocessing as mp
from multiprocessing.dummy import Pool as ThreadPool


@enum.unique
class Arms(enum.Enum):
    # 一万步兵
    infantry = 0
    lightTank = 1
    mediumTank = 2
    heavyTank = 3
    # 自行火炮
    selfPropelledGun = 4
    # 无人机
    UAV = 5


# 策略
class Ploy:
    """
    Ploy 策略
    """

    '''
    火力映射表
    兵种->单位数量武器火力值
    '''
    fireMap = {
        # 一万步兵
        Arms.infantry: 4.44,
        Arms.lightTank: 1.01,
        Arms.mediumTank: 1.14,
        Arms.heavyTank: 1.92,
        Arms.selfPropelledGun: 0.047 * 20,
        Arms.UAV: 1.25,
    }

    # 求解的目标阵营
    targetCamp = 'blue'

    @staticmethod
    def getPointMap(camp=None):
        if camp is None:
            return data.pointMap
        return getattr(data, f'{camp}PointMap')

    @staticmethod
    def getEnemyPointMap(camp):
        """
        获取敌方驻点
        :param camp:
        :return:
        """
        return Ploy.getPointMap('blue' if camp == 'red' else 'red')

    @staticmethod
    def getMyPointMap(camp):
        """
        获取我方驻点
        :param camp:
        :return:
        """
        return Ploy.getPointMap(camp)

    def initId2PointTable(self):
        """
        初始化 id->point哈希表
        :return:
        """
        self.pointMap = self.getPointMap()
        self.myPointMap = self.getPointMap(self.targetCamp)
        self.enemyPointMap = self.getPointMap('blue' if self.targetCamp == 'red' else 'red')
        return self.pointMap

        # # 每次重新计算
        # pointMap = {}
        # for row in tuple(self.sheet_point_list.values)[1:]:
        #     id_ = int(row[0])
        #     x = float(row[1])
        #     y = float(row[2])
        #     camp = row[3]
        #     BeAttackDifficulty = float(row[4])
        #     pointMap[id_] = {
        #         'x': x,
        #         'y': y,
        #         'camp': camp,
        #         'BeAttackDifficulty': BeAttackDifficulty
        #     }
        # self.pointMap = pointMap

    def initXlsx(self):
        """
        加载表格
        :return:
        """
        wb = load_workbook('../1.xlsx')
        sheets = wb.worksheets
        self.sheet_point_list = sheets[0]
        self.sheet_distance = sheets[1]

    def initMatrix(self, camp):
        """
        初始化计算所有矩阵
        :return:
        """
        # self.adjacencyMatrix = adjacencyMatrix
        # [self.distanceMatrix, self.routeMatrix] = floyd(self.adjacencyMatrix)
        [self.adjacencyMatrix, self.distanceMatrix] = [
            getattr(data, f'{camp}CampAdjacencyMatrix'),
            getattr(data, f'{camp}CampDistanceMatrix')
        ]
        return [self.adjacencyMatrix, self.distanceMatrix]

    def initWeaponParam(self, weaponParam, weaponSizeParam):
        for pointId, weaponType in enumerate(weaponParam):
            self.pointMap[str(pointId + 1)]['weaponType'] = int(weaponParam[pointId])
            self.pointMap[str(pointId + 1)]['weaponSize'] = int(weaponSizeParam[pointId])

    def __init__(self, weaponParam, weaponSizeParam, camp='blue'):
        """
        :param weaponParam: 兵种部署情况
        :param weaponSizeParam: 兵种数量情况
        """
        # self.initXlsx()
        self.initId2PointTable()
        self.initMatrix(camp)
        self.initWeaponParam(weaponParam, weaponSizeParam)

    def getDistance(self, pointId1, pointId2) -> float:
        """
        计算两点之间的距离
        :param pointId1:
        :param pointId2:
        :return:
        """
        return float(self.distanceMatrix[pointId1][pointId2])

    def getComputedFireParam(self, pointId: int) -> float:
        """
        获取计算火力值
        计算火力值 = 单位武器火力 * 武器数量
        :param pointId:
        :return:
        """
        return Ploy.getFireParamValue(self.pointMap[str(pointId + 1)]['weaponType'],
                                      self.pointMap[str(pointId)]['weaponSize'])

    def getFireParam(self, pointId: int) -> float:
        """
        获取火力系数
        :param pointId:
        :return:
        """
        weaponTypeIndex = self.pointMap[str(pointId + 1)]['weaponType']
        return Ploy.getFireParamValue(tuple(Arms)[weaponTypeIndex])

    @staticmethod
    def getFireParamValue(weaponType: Arms, weaponSize: int = 1) -> float:
        """
        获取火力参数
        :param weaponType: 兵种或者武器类型
        :param weaponSize: 武器数量
        :return: 单位数量武器火力值
        """
        return Ploy.fireMap[weaponType] * weaponSize

    def getWeaponSizeParam(self, pointId: int) -> int:
        """
        获取一点的兵力数量
        :param pointId:
        :return:
        """
        return self.pointMap[str(pointId + 1)]['weaponSize']

    def getBeAttackedDifficultyParam(self, pointId: int) -> float:
        """
        获取一点的被攻击难度
        :param pointId:
        :return:
        """
        return self.pointMap[str(pointId + 1)]['BeAttackDifficulty']

    def isConnected(self, pointId1: int, pointId2: int) -> bool:
        """
        判断两点之间是否连通
        :param pointId1:
        :param pointId2:
        :return:
        """
        return self.getDistance(pointId1, pointId2) != np.inf


class Config:
    """
    兵力限制
    """
    limit = {
        'red': {
            # 单位：2000
            Arms.infantry: 625,
            Arms.lightTank: 420,
            Arms.mediumTank: 300,
            Arms.heavyTank: 180,
            # 单位：20
            Arms.selfPropelledGun: 350,
            Arms.UAV: 500,
        },
        'blue': {
            # 单位：2000
            Arms.infantry: 500,
            # 单位：2
            Arms.lightTank: 400,
            Arms.mediumTank: 570,
            Arms.heavyTank: 340,
            # 单位：40
            Arms.selfPropelledGun: 350,
            Arms.UAV: 300,
        }
    }

    """
    当前求解阵营
    """
    targetCamp = 'blue'

    """
    当前阵营驻点数量
    """
    pointSize = 0

    """
    兵种类型数量
    """
    armTypeSize = 0

    callTimes = 0

    @staticmethod
    def getLimit() -> int:
        return math.ceil(np.array(list(Config.limit[Config.targetCamp].values())).mean() / Config.pointSize) * 2

    @staticmethod
    def getPointList() -> dict:
        """
        获取己方阵营驻点数量
        :return:
        """
        return Ploy.getMyPointMap(Config.targetCamp)


class MyProblem2(ea.Problem):  # 继承Problem父类
    """
    max f1 威胁系数之和
    max f2 安全系数之和
    s.t.
    兵种数量限制

    各点兵种 a0,a1,a2,a3,a4 ∈ {0,1,2,3,4,5}
    各点兵力数量 b0,b1,b2,b3,b4 ∈ {0,1,2,...,8225}
    各方布置10个防空点
    """

    def __init__(self, M=2, PoolType='Thread'):
        """
        :param M: 目标函数个数
        :param PoolType:
        """
        # 当前阵营驻点数量
        Config.pointSize = len(Config.getPointList())
        # 兵种类型数量
        Config.armTypeSize = len(tuple(Arms))

        name = 'MyProblem2'  # 初始化name（函数名称，可以随意设置）
        Dim = Config.pointSize * 2  # 初始化Dim（决策变量维数）
        maxormins = [-1] * M  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，0：实数；1：整数）
        lb = [0] * Dim  # 决策变量下界
        ub = [Config.armTypeSize - 1] * Config.pointSize + [Config.getLimit()] * Config.pointSize  # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self,
                            name,
                            M,
                            maxormins,
                            Dim,
                            varTypes,
                            lb,
                            ub,
                            lbin,
                            ubin)

        # 设置用多线程还是多进程
        self.PoolType = PoolType
        if self.PoolType == 'Thread':
            self.pool = ThreadPool(mp.cpu_count() * 2)  # 设置池的大小
        elif self.PoolType == 'Process':
            self.pool = ProcessPool(mp.cpu_count())  # 设置池的大小

    def evalVars(self, Vars):  # 目标函数，采用多线程加速计算
        # needTimeStart = time.time()

        N = Vars.shape[0]
        args = list(zip(Vars, list(range(N))))
        resultList = list(self.pool.map(subVars, args))
        fList = [i[0].tolist()[0] for i in resultList]
        CVList = [i[1].tolist() for i in resultList]
        f, CV = [np.array(fList), np.array(CVList)]

        # self.callTimes += 1
        # print(f'callTimes: {self.callTimes}, needTime: {time.time() - needTimeStart}')
        # print(CV)
        return f, CV


def subVars(args):
    # needTimeStart = time.time()

    Vars, indexN = args
    f1 = []
    f2 = []
    # 当前预测的策略个数
    polySize = 1

    var = Vars
    '''
    遍历每种方案
    '''

    # 各点兵种 a0,a1,a2,a3,a4 ∈ {0,1,2,3,4,5}
    everyPointWeaponRowList = var[:Config.pointSize]
    # 各点兵力数量 b0,b1,b2,b3,b4 ∈ {0,1,2,...,100}
    everyPointWeaponSizeRowList = var[Config.pointSize:]

    '''建立当前策略方案模型'''
    ploy = Ploy(everyPointWeaponRowList, everyPointWeaponSizeRowList, Config.targetCamp)
    pointIdList = tuple(range(ploy.adjacencyMatrix.shape[0]))

    '''
    max f1 当前方案的威胁系数之和
    '''
    totalDangerScore = 0
    for iPointId in pointIdList:
        '''
        遍历每个点，计算当前点i的威胁系数
        描述：
            威胁系数和自身装备实力以及距离其他点的距离有关
        '''
        # i点的威胁系数
        currentDangerScore = 0

        # 当前点火力参数
        fireParam = ploy.getFireParam(iPointId)
        # 当前点兵力数量
        weaponSizeParam = ploy.getWeaponSizeParam(iPointId)
        # 当前点被攻击难度
        beAttackedDifficultyParam = ploy.getBeAttackedDifficultyParam(iPointId)
        # 距离平衡系数
        K = 10000
        for jPointId in pointIdList:
            if jPointId == iPointId:
                continue
            # 遍历其他点，计算i点与j点的连通性

            # 其他点到当前点是否连通
            isConnectedParam = ploy.isConnected(iPointId, jPointId)

            # j点对i点的威胁系数贡献
            value = (fireParam * weaponSizeParam * isConnectedParam) / (K * beAttackedDifficultyParam)

            currentDangerScore += min(value, 1)

        totalDangerScore += currentDangerScore
    f1.append(totalDangerScore)

    '''
    max f2 当前方案的安全系数之和
    '''
    # 遍历所有点
    totalSafeScore = 0
    for iPointId in pointIdList:
        '''
        遍历每个点，计算当前点安全系数
        描述：
            当前点的安全系数是由其他所有点来决定的，和自身无关
        '''
        # 当前点i的安全系数
        currentSafeScore = 0

        # 距离平衡系数
        K = 10000

        # 遍历其他点
        for jPointId in pointIdList:
            if jPointId == iPointId:
                continue
            # 计算其他点

            # 其他点火力参数
            fireParam = ploy.getFireParam(jPointId)
            # 其他点兵力数量
            weaponSizeParam = ploy.getWeaponSizeParam(jPointId)
            # 其他点到当前点的距离
            distanceSumParam = ploy.getDistance(jPointId, iPointId)
            # 其他点到当前点是否连通
            isConnectedParam = ploy.isConnected(jPointId, iPointId)

            # j点对i点的安全系数贡献
            value = (fireParam * weaponSizeParam * isConnectedParam) / (K * distanceSumParam)

            # 合并贡献
            currentSafeScore += value

        # 计算当前方案的总安全系数
        totalSafeScore += currentSafeScore
    f2.append(totalSafeScore)

    f1 = np.array(np.matrix(f1).T)
    f2 = np.array(np.matrix(f2).T)
    f = np.hstack([f1, f2])

    # 利用可行性法则处理约束条件
    # 构建违反约束程度矩阵
    """
    max f1 威胁系数之和
    max f2 安全系数之和
    s.t.
    兵种数量限制

    各点兵种 a0,a1,a2,a3,a4 ∈ {0,1,2,3,4,5}
    各点兵力数量 b0,b1,b2,b3,b4 ∈ {0,1,2,...,8225}
    各方布置10个防空点
    """
    # 各点兵种 a0,a1,a2,a3,a4 ∈ {0,1,2,3,4,5}
    everyPointWeaponRowList = Vars[[i for i in range(0, Config.pointSize)]]
    # 各点兵力数量 b0,b1,b2,b3,b4 ∈ {0,1,2,...,100}
    everyPointWeaponSizeRowList = Vars[[i for i in range(Config.pointSize, Config.pointSize * 2)]]
    '''
    各个兵种使用数量
    '''
    everyWeaponCounter = [
        0 for i in range(len(tuple(Arms)))
    ]
    for weaponType in Arms:
        indexList = np.where(everyPointWeaponRowList == weaponType.value)
        currentWeaponCounter = 0
        for i in indexList[0]:
            currentWeaponCounter += everyPointWeaponSizeRowList[i]

        everyWeaponCounter[weaponType.value] = currentWeaponCounter

    CV_ = np.array(everyWeaponCounter)
    """
    违反约束程度矩阵
    """
    CV = []
    for weaponType in Arms:
        currentCV = CV_[[weaponType.value]]
        CV.append(currentCV - Config.limit[Config.targetCamp][weaponType])

    CV = np.hstack(CV)

    # self.callTimes += 1
    # print(f' threadId: {indexN}, callTimes: {self.callTimes}, needTime: {time.time() - needTimeStart}')
    return f, CV

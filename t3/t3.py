from typing import List
import numpy as np
from openpyxl import load_workbook
import data.t1_1_data as data
from util import Floyd
import pandas as pd

wb = load_workbook('./supplyAllocation.xlsx')
supplyAllocationSheet = wb.worksheets[0]
supplyAllocation = np.array(list(supplyAllocationSheet.values))[17:, :4]


def getSupplyAllocation(pointId: int) -> List[int]:
    """

    :param pointId: 0为第一个下标
    :return:
    """
    return list(supplyAllocation[pointId][1:])


def calcWeight(fromId: int, toId: int, distance: float) -> float:
    """
    计算权重 不利值
    :param fromId: 出发点 0为第一个下标
    :param toId: 目标点 0为第一个下标
    :param distance: 原邻接矩阵中的距离
    :return: 权重
    """
    weight = 0

    pointMap = data.pointMap
    beAttackDifficulty = pointMap[str(toId + 1)]['BeAttackDifficulty']
    materialValue = np.sum(np.array(getSupplyAllocation(toId)))

    K1 = 0.5
    K2 = 1
    K3 = 0.001
    weight = (distance * K1 + beAttackDifficulty * K2) / ((materialValue * K3) if (materialValue * K3) != 0 else 1)
    K = 10
    weight *= K
    return weight


if __name__ == '__main__':
    """
    红队进攻方案
    
    重新构建图
    权值(击败之后的收益) = (物资价值) / (路线长度*k1+攻击难度*k2)
    """
    globalAdjacencyMatrix = data.globalAdjacencyMatrix

    for rowIndex in range(len(globalAdjacencyMatrix)):
        for colIndex in range(len(globalAdjacencyMatrix)):
            currentWeight = globalAdjacencyMatrix[rowIndex][colIndex]
            if currentWeight == 0 or currentWeight == np.inf:
                continue
            globalAdjacencyMatrix[rowIndex][colIndex] = calcWeight(rowIndex, colIndex, currentWeight)

    floyd = Floyd.Floyd()
    floyd.run(globalAdjacencyMatrix)

    '''
    显示各个攻击点到基地行走路线
    '''
    blueBasePointIndex = 76
    breakthrougIndexhList = [111, 120, 98, 331, 292, 276]
    routeList = []

    for breakPoint in breakthrougIndexhList:
        result = floyd.getPath(breakPoint - 1, blueBasePointIndex - 1)
        routeList.append((np.array(result) + 1).tolist())

    '''
    导出Excel
    '''
    with open('Red Team Attack Plan.csv', 'w+') as f:
        for idx, row in enumerate(routeList):
            f.write(','.join(map(str, [breakthrougIndexhList[idx], '', *row])) + '\n')

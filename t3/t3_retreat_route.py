"""
蓝方各个节点到各个撤离点的最短距离路线
"""

import numpy as np
import data.t1_1_data as data
from util import Floyd

if __name__ == '__main__':
    globalAdjacencyMatrixButBroken = data.globalAdjacencyMatrixButBroken

    floyd = Floyd.Floyd()
    distanceMatrix, routeMatrix = floyd.run(globalAdjacencyMatrixButBroken)

    exitPointIndex = [140, 37, 378]
    routeList = []

    for exitPoint in exitPointIndex:
        for currentPoint in range(1, len(globalAdjacencyMatrixButBroken) + 1):
            result = floyd.getPath(currentPoint - 1, exitPoint - 1)
            routeList.append((np.array(result) + 1).tolist())

    '''
    蓝方各个节点到各个撤离点的最短距离路线
    '''
    with open('蓝方各个节点到各个撤离点的最短距离路线.csv', 'w+') as f:
        for idx, row in enumerate(routeList):
            f.write(','.join(map(str, row)) + '\n')

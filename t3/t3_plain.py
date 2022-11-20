"""
只考虑路程，求进攻点到基地的最短路径
"""

import numpy as np
import data.t1_1_data as allData
from util import Floyd

if __name__ == '__main__':
    floyd = Floyd.Floyd()
    floyd.run(allData.globalAdjacencyMatrix)
    '''
    显示各个攻击点到基地行走路线
    '''
    blueBasePointIndex = 76
    breakthrougIndexhList = [111, 120, 98, 331, 292, 276]
    routeList = []

    for breakPoint in breakthrougIndexhList:
        result = floyd.getPath(breakPoint - 1, blueBasePointIndex - 1)
        routeList.append(np.array(result) + 1)

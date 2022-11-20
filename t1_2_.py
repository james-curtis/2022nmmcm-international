# %%
"""
这个文件是算整个图的邻接矩阵
"""
# 以及双方的最佳指挥阵地和几个备选阵地
import numpy as np
import json
from openpyxl import load_workbook
import networkx as nx
import matplotlib.pyplot as plt


def floyd(adjacent_matrix):
    distance = np.array(adjacent_matrix, copy=True)  # 邻接矩阵包含了任意两个节点之间的距离，distance
    n = adjacent_matrix.shape[0]
    route = np.zeros(adjacent_matrix.shape)  # 初始化路由矩阵，让它都是零
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distance[i][k] + distance[k][j] < distance[i][j]:
                    distance[i][j] = distance[i][k] + distance[k][j]  # 找到经过k点时路径更短，接受这个更短的路径长度
                    route[i][j] = k  # 路由矩阵记录路径
    return distance, route


# %%
# Annex1：node＆link.xlsx
wb = load_workbook('1.xlsx')
sheets = wb.worksheets
sheet_point_list = sheets[0]
sheet_distance = sheets[1]
distanceList = np.array(list(sheet_distance.values)[1:])

# %%
# 构建邻接矩阵
maxPoint = distanceList.shape[0]

# 邻接矩阵
adjacencyMatrix = np.zeros((maxPoint, maxPoint))

# A     B       C   D
# id	from	to	length(km)
for row in tuple(distanceList.tolist())[1:]:
    fromId = row[1]
    toId = row[2]
    length = row[3]
    adjacencyMatrix[int(fromId - 1)][int(toId - 1)] = length
    adjacencyMatrix[int(toId - 1)][int(fromId - 1)] = length

for rowLine, rowData in enumerate(adjacencyMatrix):
    for colLine, cellData in enumerate(rowData):
        if cellData == 0:
            rowData[colLine] = np.inf
            # rowData[colLine] = 0
        if rowLine == colLine:
            rowData[colLine] = 0

adjacencyMatrixJson = json.dumps(adjacencyMatrix.tolist())
# with open('./data/globalAdjacencyMatrix.json', 'w+') as f:
#     f.write(adjacencyMatrixJson)

# %%
# Floyd算法计算

# 距离矩阵      路由矩阵
distanceMatrix, routeMatrix = floyd(adjacencyMatrix)
distanceMatrixJson = json.dumps(distanceMatrix.tolist())

print('计算完成')

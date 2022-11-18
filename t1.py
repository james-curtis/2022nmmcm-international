#%%
# 以及双方的最佳指挥阵地和几个备选阵地
import numpy as np
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
# 测试数据
adjacencyMatrix = np.array([[0, 3, np.inf, 2, np.inf],
                            [3, 0, 2, 1, np.inf],
                            [np.inf, 2, 0, np.inf, 5],
                            [2, 1, np.inf, 0, 4],
                            [np.inf, np.inf, 5, 4, 0]])
distanceMatrix, routeMatrix = floyd(adjacencyMatrix)

# %%
# Annex1：node＆link.xlsx
wb = load_workbook('1.xlsx')
sheets = wb.worksheets
sheet_point_list = sheets[0]
sheet_distance = sheets[1]
# 求解的目标阵营
targetCamp = 'blue'

# %%
# id->阵营哈希表
campMap = {}
for row in tuple(sheet_point_list.values)[1:]:
    camp = row[3]
    id_ = row[0]
    campMap[id_] = camp

# %%
# 数据处理
# 单独计算某一方，过滤另一方并修改id

# 红方剔除孤立点剔除
exceptList = '159 1 24 4 23 18 5 17 20 12 19 16 13 21 22 15 11 8 10 9 6 14 7'.split()
exceptList = np.array(exceptList, dtype=int)
pointList = []
for row in list(sheet_point_list.values)[1:]:
    if row[0] in exceptList:
        continue
    pointList.append(row)

# 先在距离表中剔除敌方点
pointList = np.array(pointList)
# 敌方id列表
enemyIdList = np.array(pointList[pointList[:, -2] != targetCamp][:, 0], dtype=int).tolist()
# 己方id列表
myIdList = np.array(pointList[pointList[:, -2] == targetCamp][:, 0], dtype=int).tolist()

# 两个坐标表相互对照id
pointFilterList = pointList[pointList[:, -2] == targetCamp]  # 己方坐标表
pointFilterListIndexValues = np.array(pointFilterList[:, 0], dtype=int).tolist()
pointFilterReOrderList = pointFilterList.copy()  # 己方id重新按顺序填充 坐标表
for index, row in enumerate(pointFilterReOrderList):
    row[0] = index + 1
pointFilterReOrderListIndexValues = np.array(pointFilterReOrderList[:, 0], dtype=int).tolist()

distanceList = np.array(list(sheet_distance.values)[1:])
# 在距离表中将要删除的索引列表，所有涉及到敌方坐标的点全部删除
distanceListWillDeleteIndexList = set()
for index, row, in enumerate(distanceList):
    fromId = int(row[1])
    toId = int(row[2])
    # 在己方距离表中剔除关联了地方的点
    if fromId in enemyIdList or toId in enemyIdList:
        distanceListWillDeleteIndexList.add(index)
        continue
    if fromId in exceptList or toId in exceptList:
        distanceListWillDeleteIndexList.add(index)
        continue
    # 把fromId和toId替换成对应重排后的id
    pos = pointFilterListIndexValues.index(fromId)
    row[1] = pointFilterReOrderListIndexValues[pos]

    pos = pointFilterListIndexValues.index(toId)
    row[2] = pointFilterReOrderListIndexValues[pos]
# 删除涉及敌方id的行
distanceList: np.ndarray = np.delete(distanceList, list(distanceListWillDeleteIndexList), 0)

# %%
# 构建邻接矩阵
maxPoint = len(myIdList)

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

# %%
# Floyd算法计算

# 距离矩阵      路由矩阵
distanceMatrix, routeMatrix = floyd(adjacencyMatrix)

print()

# 在第一列和第一行添加对应的坐标映射
resultMatrix = np.insert(distanceMatrix, 0, pointFilterList[:, 0], axis=0)
resultMatrix = np.insert(resultMatrix, 0, np.insert(pointFilterList[:, 0], 0, [0]), axis=1)

# %%
# @link https://blog.csdn.net/weixin_52365731/article/details/117048879
# 判断连通图

# adjacencyMatrix = np.array([[0, 3, 0, 2, 0],
#                             [3, 0, 2, 1, 0],
#                             [0, 2, 0, 0, 5],
#                             [2, 1, 0, 0, 4],
#                             [0, 0, 5, 4, 0]])

n = adjacencyMatrix.shape[0]  # 输入矩阵的行列数
x = np.array(adjacencyMatrix, dtype=int)  # 利用numpy库将输入的列表转换为numpy中矩阵
value_1 = value_2 = sum_1 = sum_2 = sum_3 = sum_4 = y = final = x  # 分别定义value_1,sum_1,sum_2等变量(这里代码写的很恶心）
y = x + x.T
# ---------------------------------------------------------------------
for i in range(1, n):  # 计算可达矩阵-此处可参考上图所给出的可达矩阵数学求解方法
    value_1 = np.matmul(value_1, x)
    sum_1 = sum_1 + value_1
sum_2 = sum_1 + np.identity(n)

reachability_matrix = sum_2 > 0.5  # 此处将其sum_2矩阵中所有大于0.5的矩阵元素转换为布尔值True，其余元素(均为0)转换为False

print("此有向图的可达矩阵为：")
print(reachability_matrix.astype(int))  # 得到布尔型矩阵，可将布尔类型数据(True-False)相应转化为数值型(0-1)矩阵-即可达矩阵

final = reachability_matrix + reachability_matrix.T

for i in range(1, n):  # 同上，其实应该编个函数
    value_2 = np.matmul(value_2, y)
    sum_3 = sum_3 + value_2
sum_4 = sum_3 + np.identity(n)
reachability_matrix_1 = sum_4 > 0.5
# ---------------------------------------------------------------------
# 给出判断结果
if ((reachability_matrix.astype(int) == np.ones((n, n)).astype(int)).all()):
    print("此有向线图G为强连通图或其为无向连通图")
    # print(np.ones((n,n)).astype(int))默认生成全1矩阵其中元素为float型，要多加注意
elif ((final.astype(int) == np.ones((n, n)).astype(int)).all()):
    print("此有向线图G是单向连通图")
elif ((reachability_matrix_1.astype(int) == np.ones((n, n)).astype(int)).all()):
    print("此有向线图G是弱连通图")
else:
    print("此有向图不连通")

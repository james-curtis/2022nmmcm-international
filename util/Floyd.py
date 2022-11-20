import numpy as np


class Floyd:
    def run(self, adjacencyMatrix):
        distanceMatrix = np.array(adjacencyMatrix, copy=True)
        n = len(distanceMatrix)
        routeMatrix = [[i] * n for i in range(n)]  # 关键地方，i-->j 的父结点初始化都为i
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if distanceMatrix[i][k] + distanceMatrix[k][j] < distanceMatrix[i][j]:
                        distanceMatrix[i][j] = distanceMatrix[i][k] + distanceMatrix[k][j]
                        routeMatrix[i][j] = routeMatrix[k][j]  # 更新父结点
        self.distanceMatrix = distanceMatrix
        self.routeMatrix = routeMatrix
        return distanceMatrix, routeMatrix

    def getPath(self, fromId, toId, routeMatrix=None):
        routePath = []
        if routeMatrix is None:
            routeMatrix = self.routeMatrix

        def get(i, j, route):
            if i != j:
                get(i, route[i][j], route)
            routePath.append(j)

        get(fromId, toId, routeMatrix)
        return routePath

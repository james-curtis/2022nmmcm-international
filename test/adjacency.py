import data.t1_1_data as da
import numpy as np
import json


da.globalAdjacencyMatrix[292 - 1][286 - 1] = np.inf
da.globalAdjacencyMatrix[276 - 1][275 - 1] = np.inf
da.globalAdjacencyMatrix[331 - 1][101 - 1] = np.inf
da.globalAdjacencyMatrix[98 - 1][99 - 1] = np.inf
da.globalAdjacencyMatrix[98 - 1][116 - 1] = np.inf
da.globalAdjacencyMatrix[111 - 1][128 - 1] = np.inf
da.globalAdjacencyMatrix[111 - 1][110 - 1] = np.inf
da.globalAdjacencyMatrix[120 - 1][100 - 1] = np.inf

da.globalAdjacencyMatrix[286 - 1][292 - 1] = np.inf
da.globalAdjacencyMatrix[275 - 1][276 - 1] = np.inf
da.globalAdjacencyMatrix[101 - 1][331 - 1] = np.inf
da.globalAdjacencyMatrix[99 - 1][98 - 1] = np.inf
da.globalAdjacencyMatrix[116 - 1][98 - 1] = np.inf
da.globalAdjacencyMatrix[128 - 1][111 - 1] = np.inf
da.globalAdjacencyMatrix[110 - 1][111 - 1] = np.inf
da.globalAdjacencyMatrix[100 - 1][120 - 1] = np.inf

j = json.dumps(da.globalAdjacencyMatrix.tolist())
print()
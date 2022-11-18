graph = {'A': [(7, 'A', 'B'), (5, 'A', 'D')],
         'B': [(7, 'B', 'A'), (8, 'B', 'C'), (9, 'B', 'D'), (7, 'B', 'E')],
         'C': [(8, 'C', 'B'), (5, 'C', 'E')],
         'D': [(5, 'D', 'A'), (9, 'D', 'B'), (15, 'D', 'E'), (6, 'D', 'F')],
         'E': [(7, 'E', 'B'), (5, 'E', 'C'), (15, 'E', 'D'), (8, 'E', 'F'), (9, 'E', 'G')],
         'F': [(6, 'F', 'D'), (8, 'F', 'E'), (11, 'F', 'G')],
         'G': [(9, 'G', 'E'), (11, 'G', 'F')]
         }


def graph2adjacent_matrix(graph):
    vnum = len(graph)
    dict = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}
    adjacent_matrix = [[0 if row == col else float('inf') for col in range(vnum)] for row in range(vnum)]
    vertices = graph.keys()
    for vertex in vertices:
        for edge in graph[vertex]:
            w, u, v = edge
            adjacent_matrix[dict.get(u)][dict.get(v)] = w
    return adjacent_matrix


def floyd(adjacent_matrix):
    vnum = len(adjacent_matrix)
    a = [[adjacent_matrix[row][col] for col in range(vnum)] for row in range(vnum)]
    nvertex = [[-1 if adjacent_matrix[row][col] == float('inf') else col for col in range(vnum)] for row in range(vnum)]
    # print(adjacent_matrix)
    for k in range(vnum):
        for i in range(vnum):
            for j in range(vnum):
                if a[i][j] > a[i][k] + a[k][j]:
                    a[i][j] = a[i][k] + a[k][j]
                    nvertex[i][j] = nvertex[i][k]
    return nvertex, a


adjacent_matrix = graph2adjacent_matrix(graph)
nvertex, a = floyd(adjacent_matrix)
print(adjacent_matrix)

# ### 打印经过的顶点 ###
# print()
# for i in range(len(nvertex)):
#     for j in range(len(nvertex[0])):
#         print(nvertex[i][j], end="\t")
#     print()  # 打印一行后换行
# ### 打印彼此之间的最短距离 ###
# print()
# for i in range(len(a)):
#     for j in range(len(a[0])):
#         print(a[i][j], end="\t")
#     print()  # 打印一行后换行

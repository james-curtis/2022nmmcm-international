import random

from MyProblem import *  # 导入自定义问题接口

import geatpy as ea  # import geatpy

if __name__ == '__main__':
    # 实例化问题对象
    problem = MyProblem2()
    # 构建算法
    algorithm = ea.soea_SGA_templet(
        problem,
        ea.Population(Encoding='BG',  # 种群的染色体是'BG'编码
                      NIND=100),  # 种群数量
        MAXGEN=1000,  # 最大进化代数
        logTras=1)  # 表示每隔多少代记录一次日志信息，0表示不记录。
    # algorithm.mutOper.Pm = 0.2  # 修改变异算子的变异概率
    # algorithm.recOper.XOVR = 0.7  # 修改交叉算子的交叉概率
    # 求解
    res = ea.optimize(algorithm,
                      seed=random.randint(1, 9999),
                      verbose=True,
                      drawing=1,
                      outputMsg=True,
                      drawLog=True,
                      saveFlag=True,
                      dirName='result')
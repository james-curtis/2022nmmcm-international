import json

from openpyxl import load_workbook

wb = load_workbook('../1.xlsx')
sheets = wb.worksheets
sheet_point_list = sheets[0]
sheet_distance = sheets[1]
# 求解的目标阵营

pointMap = {}
for row in tuple(sheet_point_list.values)[1:]:
    id_ = int(row[0])
    x = float(row[1])
    y = float(row[2])
    camp = row[3]
    BeAttackDifficulty = float(row[4])
    pointMap[id_] = {
        'x': x,
        'y': y,
        'camp': camp,
        'BeAttackDifficulty': BeAttackDifficulty
    }

bluePointMap = {}
for row in tuple(sheet_point_list.values)[1:]:
    id_ = int(row[0])
    x = float(row[1])
    y = float(row[2])
    camp = row[3]
    BeAttackDifficulty = float(row[4])
    if camp != 'blue':
        continue
    bluePointMap[id_] = {
        'x': x,
        'y': y,
        'camp': camp,
        'BeAttackDifficulty': BeAttackDifficulty
    }

redPointMap = {}
for row in tuple(sheet_point_list.values)[1:]:
    id_ = int(row[0])
    x = float(row[1])
    y = float(row[2])
    camp = row[3]
    BeAttackDifficulty = float(row[4])
    if camp != 'red':
        continue
    redPointMap[id_] = {
        'x': x,
        'y': y,
        'camp': camp,
        'BeAttackDifficulty': BeAttackDifficulty
    }

with open('./pointMap.json', mode='w+') as f:
    f.write(json.dumps(pointMap))
with open('./redPointMap.json', mode='w+') as f:
    f.write(json.dumps(redPointMap))
with open('./bluePointMap.json', mode='w+') as f:
    f.write(json.dumps(bluePointMap))

print('导出完成')


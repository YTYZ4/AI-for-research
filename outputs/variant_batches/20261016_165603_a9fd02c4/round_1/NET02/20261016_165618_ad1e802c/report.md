# 图与网络求解报告

输水网络最大流

任务：max_flow；起点：S；终点：T；单位：立方米/小时。
所有边按有向边解释；双向道路须在模型中列出两个方向。
假设：管道有向，只能沿S→A、S→B、A→B、A→T、B→T方向输水。；所有容量单位统一为立方米/小时。；中间节点A、B满足流量守恒。；需求最大总流量及各管道流量，并给出最小割验证；由求解器计算。

| 起点 | 终点 | 距离或容量 |
|---|---|---:|
| S | A | 10 |
| S | B | 5 |
| A | B | 4 |
| A | T | 6 |
| B | T | 9 |

状态：optimal；结果：15 立方米/小时。
最小割源侧：S
最小割容量：15，与最大流相等。
各边流量见 edges.csv。

验证：{'passed': True, 'checks': {'capacity_bounds': True, 'conservation': True, 'source_target_balance': True, 'flow_equals_cut': True, 'cut_separates': True}}

证据只针对生成的图；仍须对照原题核对方向、缺边、权重与单位。当前不支持负权、平行边、多商品流或成本流。

# 图与网络求解报告

有向道路网络最短路径

任务：shortest_path；起点：S；终点：T；单位：kilometer。
所有边按有向边解释；双向道路须在模型中列出两个方向。
假设：所有道路均为有向边，只能沿给定方向行驶。；边权为道路长度，单位统一为千米。

| 起点 | 终点 | 距离或容量 |
|---|---|---:|
| S | A | 4 |
| S | B | 2 |
| B | A | 1 |
| A | C | 2 |
| B | C | 5 |
| C | T | 3 |
| A | T | 7 |

状态：optimal；结果：8 kilometer。
路径：S → B → A → C → T
距离标签（null为不可达）：{'S': 0, 'A': 3, 'B': 2, 'C': 5, 'T': 8}

验证：{'passed': True, 'checks': {'reachable_set_closed': True, 'distance_inequalities': True, 'path_matches_distance': True}}

证据只针对生成的图；仍须对照原题核对方向、缺边、权重与单位。当前不支持负权、平行边、多商品流或成本流。

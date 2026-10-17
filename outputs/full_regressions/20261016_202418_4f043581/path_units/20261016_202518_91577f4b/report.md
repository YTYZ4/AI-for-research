# 图与网络求解报告

shortest_path_S_to_T

任务：shortest_path；起点：S；终点：T；单位：meter。
所有边按有向边解释；双向道路须在模型中列出两个方向。
假设：所有边均为单向有向边，方向严格按给定列表，不增加任何反向边或其它道路。；距离单位统一为米，2千米=2000米，3千米=3000米，7千米=7000米。

| 起点 | 终点 | 距离或容量 |
|---|---|---:|
| S | A | 4000 |
| S | B | 2000 |
| B | A | 1000 |
| A | C | 2000 |
| B | C | 5000 |
| C | T | 3000 |
| A | T | 7000 |

状态：optimal；结果：8000 meter。
路径：S → B → A → C → T
距离标签（null为不可达）：{'S': 0, 'A': 3000, 'B': 2000, 'C': 5000, 'T': 8000}

验证：{'passed': True, 'checks': {'reachable_set_closed': True, 'distance_inequalities': True, 'path_matches_distance': True}}

证据只针对生成的图；仍须对照原题核对方向、缺边、权重与单位。当前不支持负权、平行边、多商品流或成本流。

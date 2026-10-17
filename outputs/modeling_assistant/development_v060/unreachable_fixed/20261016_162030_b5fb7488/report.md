# 图与网络求解报告

S到T最短路径

任务：shortest_path；起点：S；终点：T；单位：km。
所有边按有向边解释；双向道路须在模型中列出两个方向。
假设：有向道路网络，道路均为有向边；用户声明没有其他道路，因此仅保留已给出的边；节点T在给定边集中孤立，求解器将报告不可达

| 起点 | 终点 | 距离或容量 |
|---|---|---:|
| S | A | 2 |

状态：unreachable；结果：None km。
终点不可达。
距离标签（null为不可达）：{'S': 0, 'A': 2, 'T': None}

验证：{'passed': True, 'checks': {'reachable_set_closed': True, 'distance_inequalities': True, 'path_matches_distance': True}}

证据只针对生成的图；仍须对照原题核对方向、缺边、权重与单位。当前不支持负权、平行边、多商品流或成本流。

# 图与网络求解报告

有向输水网络最大流

任务：max_flow；起点：S；终点：T；单位：立方米/小时。
所有边按有向边解释；双向道路须在模型中列出两个方向。
假设：管道只能沿给定方向输水；中间节点满足流量守恒；S为唯一源点，T为唯一汇点；容量单位统一为立方米/小时

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

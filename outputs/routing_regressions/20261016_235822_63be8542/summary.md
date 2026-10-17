# 图结构与目标证据路由定向回归

完成42/42；原始34；格式后累计34；本地后累计39。
路径计数：{'local_guard': 5, 'failed': 3, 'native': 34}；tokens 105263；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| flow_reverse_conversion | new_boundary | 3 | 2 | 2 | 2 |
| flow_unknown_conversion | new_boundary | 3 | 1 | 1 | 3 |
| flow_missing_direction | new_boundary | 3 | 3 | 3 | 3 |
| flow_min_cost | new_boundary | 3 | 3 | 3 | 3 |
| cost_paraphrase | scope_boundary | 3 | 3 | 3 | 3 |
| cost_not_requested | negative_control | 3 | 3 | 3 | 3 |
| cost_synonym | synonym | 3 | 3 | 3 | 3 |
| throughput_synonym | synonym | 3 | 3 | 3 | 3 |
| flow_cost_priority | synonym | 3 | 2 | 2 | 2 |
| mixed_fitting | mixed | 3 | 3 | 3 | 3 |
| mixed_production | mixed | 3 | 3 | 3 | 3 |
| mixed_logistic | mixed | 3 | 2 | 2 | 2 |
| OPT01 | nongraph_control | 3 | 3 | 3 | 3 |

## 非原始通过
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_reverse_conversion #1：failed needs_clarification 原题只给出源点S、汇点T以及一条从S到T、容量为0.001立方米/小时的边，无法据此建模最大流问题；请补充完整的节点、边及每条边的容量（或确认该网络仅含这一条边？）
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_cost_priority #3：failed refusal_extra_assertions {"passed": false, "checks": {"no_task_change_suggestions": false, "no_false_missing_claims": true}, "task_change_clauses": ["支持边界：若仅求单商品最大流", "若仅求最短路径"], "false_missing_claims": []}
- mixed_logistic #3：failed refusal_semantics {"passed": false, "checks": {"unsupported": true, "no_model": true, "nonblank_explanations": true, "identifies_requested_scope": true, "explains_limit": false, "no_invented_contract_limit": true, "no_silent_downgrade": true}, "text": "该请求同时要求两类不同建模任务：图网络最大流/最低成本运输分配，以及 Logistic 动态模型需求预测；当前单模型协议不能联合表示并求解这两个任务。"}

14开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

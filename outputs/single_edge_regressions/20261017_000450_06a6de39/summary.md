# 完整单边与混合拒绝定向回归

完成45/45；原始37；格式后累计37；本地后累计43。
路径计数：{'local_guard': 6, 'native': 37, 'failed': 2}；tokens 114067；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| flow_reverse_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_unknown_conversion | new_boundary | 3 | 0 | 0 | 3 |
| flow_missing_direction | new_boundary | 3 | 1 | 1 | 1 |
| flow_min_cost | new_boundary | 3 | 3 | 3 | 3 |
| cost_paraphrase | scope_boundary | 3 | 3 | 3 | 3 |
| cost_not_requested | negative_control | 3 | 3 | 3 | 3 |
| flow_cost_priority | synonym | 3 | 3 | 3 | 3 |
| mixed_fitting | mixed | 3 | 3 | 3 | 3 |
| mixed_production | mixed | 3 | 3 | 3 | 3 |
| mixed_logistic | mixed | 3 | 3 | 3 | 3 |
| OPT01 | nongraph_control | 3 | 3 | 3 | 3 |
| single_forward | complete_boundary | 3 | 3 | 3 | 3 |
| single_zero | complete_boundary | 3 | 3 | 3 | 3 |
| single_missing_capacity | missing_boundary | 3 | 3 | 3 | 3 |

## 非原始通过
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #1：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_missing_direction #2：failed direction_semantics {"passed": false, "checks": {"clarification": true, "no_model": true, "nonblank": true, "asks_direction": false, "no_assumed_direction": true}, "text": "缺少边 S—T 的方向：最大流需要每条边的方向。"}
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_missing_direction #3：failed generation_error ValueError: 建模响应格式错误：'model' is a required property

15开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

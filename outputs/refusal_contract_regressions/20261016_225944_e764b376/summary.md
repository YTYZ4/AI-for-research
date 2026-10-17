# 非就绪响应说明契约定向回归

完成42/42；原始34；格式后累计34；本地后累计40。
路径计数：{'native': 34, 'local_guard': 6, 'failed': 2}；tokens 81621；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| immutable_lock_dont | historical_guard | 3 | 3 | 3 | 3 |
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_original_unit | control | 3 | 3 | 3 | 3 |
| flow_integer_conversion | control | 3 | 3 | 3 | 3 |
| flow_reverse_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_unknown_conversion | new_boundary | 3 | 0 | 0 | 3 |
| flow_missing_direction | new_boundary | 3 | 1 | 1 | 1 |
| flow_min_cost | new_boundary | 3 | 3 | 3 | 3 |
| pure_min_cost | scope_boundary | 3 | 3 | 3 | 3 |
| cost_paraphrase | scope_boundary | 3 | 3 | 3 | 3 |
| multi_commodity | scope_boundary | 3 | 3 | 3 | 3 |
| time_varying | scope_boundary | 3 | 3 | 3 | 3 |
| cost_not_requested | negative_control | 3 | 3 | 3 | 3 |

## 非原始通过
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #1：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_missing_direction #1：failed needs_clarification 需要明确 S 与 T 之间这条边从哪个节点指向哪个节点，才能建立有向最大流模型。
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_missing_direction #2：failed unsupported 请求为S到T的最大流，但原文仅说明S与T之间有容量1000升/小时且‘方向未知’，未提供可确定的有向边或无向边双向展开信息，因此无法构建满足最大流方向要求的原始图。支持边界：最大流要求所有边方向明确，或明确说明为无向边并可展开为两条反向边；本请求方向未知，故不支持。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。

14开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

# 零新增API的评分修订重评

同一48次历史付费响应，不是新调用；tokens为源批使用量，不重复计费统计。原批评分保留。

# 方向追问及拒绝说明定向回归

完成48/48；原始41；格式后累计41；本地后累计47。
路径计数：{'local_guard': 6, 'native': 41, 'failed': 1}；tokens 82811；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_integer_conversion | control | 3 | 3 | 3 | 3 |
| flow_reverse_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_unknown_conversion | new_boundary | 3 | 0 | 0 | 3 |
| flow_missing_direction | new_boundary | 3 | 3 | 3 | 3 |
| flow_min_cost | new_boundary | 3 | 3 | 3 | 3 |
| pure_min_cost | scope_boundary | 3 | 3 | 3 | 3 |
| cost_paraphrase | scope_boundary | 3 | 2 | 2 | 2 |
| multi_commodity | scope_boundary | 3 | 3 | 3 | 3 |
| time_varying | scope_boundary | 3 | 3 | 3 | 3 |
| cost_not_requested | negative_control | 3 | 3 | 3 | 3 |
| direction_unspecified | direction_boundary | 3 | 3 | 3 | 3 |
| direction_immutable | direction_boundary | 3 | 3 | 3 | 3 |
| direction_known | valid_direction | 3 | 3 | 3 | 3 |
| cost_missing_direction | scope_priority | 3 | 3 | 3 | 3 |

## 非原始通过
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #1：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- cost_paraphrase #1：failed refusal_semantics {"passed": false, "checks": {"unsupported": false, "no_model": true, "nonblank_explanations": true, "identifies_requested_scope": true, "explains_limit": true, "no_invented_contract_limit": true, "no_silent_downgrade": true}, "text": "该问题同时包含最大流和运输成本最小化（最小费用流），当前仅支持单一最大流或最短路径问题，不支持按“先最大流再最小费用”的多目标求解；请确认是要仅最大流，还是仅最短路径？"}
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。

16开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

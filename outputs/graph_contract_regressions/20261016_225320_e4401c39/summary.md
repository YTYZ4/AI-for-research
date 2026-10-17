# 图输入契约隔离定向回归

完成42/42；原始30；格式后累计30；本地后累计39。
路径计数：{'native': 30, 'local_guard': 9, 'failed': 3}；tokens 69020；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| immutable_lock_dont | historical_guard | 3 | 3 | 3 | 3 |
| conflict_all_negative | historical_guard | 3 | 3 | 3 | 3 |
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_original_unit | control | 3 | 3 | 3 | 3 |
| flow_integer_conversion | control | 3 | 3 | 3 | 3 |
| flow_reverse_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_same_fractional | new_boundary | 3 | 0 | 0 | 3 |
| flow_unknown_conversion | new_boundary | 3 | 0 | 0 | 3 |
| path_units | path_control | 3 | 3 | 3 | 3 |
| flow_time_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_zero_conversion | new_boundary | 3 | 3 | 3 | 3 |
| flow_missing_direction | new_boundary | 3 | 3 | 3 | 3 |
| flow_min_cost | new_boundary | 3 | 0 | 0 | 0 |

## 非原始通过
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_same_fractional #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #1：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_min_cost #1：failed generation_error ValueError: 未就绪响应必须不含模型，且说明待澄清或不支持的原因
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_same_fractional #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_min_cost #2：failed generation_error ValueError: 未就绪响应必须不含模型，且说明待澄清或不支持的原因
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_same_fractional #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_min_cost #3：failed generation_error ValueError: 未就绪响应必须不含模型，且说明待澄清或不支持的原因

14开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

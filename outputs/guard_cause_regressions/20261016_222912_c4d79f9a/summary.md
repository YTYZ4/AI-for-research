# 本地策略共因修复定向回归

完成57/57；原始49；格式后累计49；本地后累计56。
路径计数：{'native': 49, 'local_guard': 7, 'failed': 1}；tokens 295069；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| DYN02_error | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_original | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_dont | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_keep | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_cannot | historical_guard | 3 | 2 | 2 | 3 |
| immutable_negated_permission_invalid | historical_guard | 3 | 3 | 3 | 3 |
| conflict_all_negative | historical_guard | 3 | 2 | 2 | 3 |
| equivalent_same_invalid | historical_guard | 3 | 3 | 3 | 3 |
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| remaining_permission_forbidden | historical_guard | 3 | 3 | 3 | 3 |
| remaining_permission_conflict | historical_guard | 3 | 2 | 2 | 3 |
| immutable_valid_above | control | 3 | 3 | 3 | 3 |
| immutable_missing_capacity | control | 3 | 3 | 3 | 3 |
| immutable_permission | control | 3 | 3 | 3 | 3 |
| conflict_two_positive | control | 3 | 2 | 2 | 3 |
| equivalent_scientific | control | 3 | 3 | 3 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_original_unit | control | 3 | 3 | 3 | 3 |
| flow_integer_conversion | control | 3 | 2 | 2 | 2 |

## 非原始通过
- immutable_lock_cannot #1：local_guard  环境容量K=0会使Logistic方程中的N/K项无定义，当前常参数连续Logistic模型无效；原题条件保持不变，当前不执行求解，也不要求修改参数。
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- remaining_permission_conflict #1：local_guard  环境容量K的原文记录相互冲突：“环境容量恒定0个”；“K=0.5个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- conflict_two_positive #1：local_guard  环境容量K的原文记录相互冲突：“环境承载量固定0.5个”；“K=1个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- conflict_all_negative #3：local_guard  环境容量K的原文记录相互冲突：“容量恒定-1个”；“K=-2个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_integer_conversion #3：failed unsupported 原边容量为1000升/小时，换算为1立方米/小时是整数；但题目要求所有容量和结果均以立方米/小时表示，当前求解器最大流支持原题单位下的非负整数容量，无法强制统一输出单位并在该单位下完成整数校验与求解。

19开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

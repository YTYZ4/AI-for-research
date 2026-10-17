# 否定、隐含冲突与合法换算定向回归

完成66/66；原始50；格式后累计50；本地后累计61。
路径计数：{'native': 50, 'local_guard': 11, 'failed': 5}；tokens 346548；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| DYN02_error | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_original | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_dont | historical_guard | 3 | 0 | 0 | 3 |
| immutable_lock_keep | historical_guard | 3 | 3 | 3 | 3 |
| immutable_lock_cannot | historical_guard | 3 | 2 | 2 | 2 |
| immutable_negated_permission_invalid | historical_guard | 3 | 3 | 3 | 3 |
| conflict_all_negative | historical_guard | 3 | 2 | 2 | 3 |
| equivalent_same_invalid | historical_guard | 3 | 3 | 3 | 3 |
| graph_units_fractional_flow | historical_guard | 3 | 0 | 0 | 3 |
| remaining_permission_forbidden | historical_guard | 3 | 2 | 2 | 2 |
| remaining_permission_conflict | historical_guard | 3 | 3 | 3 | 3 |
| immutable_valid_above | control | 3 | 3 | 3 | 3 |
| immutable_missing_capacity | control | 3 | 3 | 3 | 3 |
| immutable_permission | control | 3 | 3 | 3 | 3 |
| conflict_two_positive | control | 3 | 3 | 3 | 3 |
| equivalent_scientific | control | 3 | 3 | 3 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_original_unit | control | 3 | 2 | 2 | 2 |
| flow_integer_conversion | control | 3 | 2 | 2 | 2 |
| flow_reverse_conversion | new_boundary | 3 | 2 | 2 | 2 |
| flow_same_fractional | new_boundary | 3 | 0 | 0 | 3 |
| flow_unknown_conversion | new_boundary | 3 | 2 | 2 | 3 |

## 非原始通过
- immutable_lock_dont #1：local_guard  环境容量K=0使Logistic方程dN/dt=rN(1-N/K)出现除零，当前模型无效；原题条件保持不变，当前不执行求解，也不要求修改参数。
- graph_units_fractional_flow #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_reverse_conversion #1：failed unsupported 原题容量为0.001立方米/小时；要求所有容量和结果以升/小时表示，统一单位换算：0.001立方米/小时 = 1升/小时。当前求解器要求最大流容量在统一输出单位下必须为整数升/小时，且明确不允许取整，因此该问题超出当前最大流求解器支持范围。
- flow_same_fractional #1：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- immutable_lock_dont #2：local_guard  当前常参数 Logistic 模型要求环境容量 K 为正实数；原题给定 K=0（环境容量恒定0个），会使模型项 rN(1-N/K) 出现除零，模型无效；原题条件保持不变，当前不执行求解，也不要求修改参数。
- immutable_lock_cannot #2：failed generation_error ValueError: 未就绪响应必须不含模型，且说明待澄清或不支持的原因
- conflict_all_negative #2：local_guard  环境容量K的原文记录相互冲突：“容量恒定-1个”；“K=-2个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- graph_units_fractional_flow #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- remaining_permission_forbidden #2：failed generation_error ValueError: 未就绪响应必须不含模型，且说明待澄清或不支持的原因
- flow_original_unit #2：failed needs_clarification 图边单位与原文引用不一致，请保留原题单位写法。
- flow_integer_conversion #2：failed needs_clarification 请确认：题目中同一条边的容量记录存在冲突还是仅有一条记录？目前仅见“S到T容量1000升/小时”，但要求统一输出立方米/小时。请确认是否允许按原题数值1000升/小时进行单位换算为1立方米/小时，还是需保留其他记录？
- flow_same_fractional #2：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- immutable_lock_dont #3：local_guard  原题条件保持不变，当前不执行求解，也不要求修改参数。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_same_fractional #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。

22开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

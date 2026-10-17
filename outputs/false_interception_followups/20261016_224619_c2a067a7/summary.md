# 否定、隐含冲突与合法换算定向回归

完成21/21；原始13；格式后累计13；本地后累计17。
路径计数：{'native': 13, 'failed': 4, 'local_guard': 4}；tokens 106971；usage未知0。

原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。

| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---|---:|---:|---:|---:|
| immutable_lock_dont | historical_guard | 3 | 3 | 3 | 3 |
| conflict_all_negative | historical_guard | 3 | 3 | 3 | 3 |
| graph_units_fractional_flow | historical_guard | 3 | 2 | 2 | 3 |
| graph_units_flow_mixed | control | 3 | 3 | 3 | 3 |
| flow_integer_conversion | control | 3 | 2 | 2 | 2 |
| flow_reverse_conversion | new_boundary | 3 | 0 | 0 | 0 |
| flow_unknown_conversion | new_boundary | 3 | 0 | 0 | 3 |

## 非原始通过
- flow_integer_conversion #1：failed unsupported 原题唯一容量为1000升/小时，要求所有容量和结果均以立方米/小时表示且不允许改变统一输出单位或取整；1000升/小时精确换算为1立方米/小时，属于整数容量，最大流问题本身在程序能力范围内，但当前 JSON Schema 的 graph_input 边字段不支持 source_quote/unit_quote 逐字引用，无法在不丢字段的情况下返回可校验的 ready 模型。
- flow_reverse_conversion #1：failed unsupported 原边容量为0.001立方米/小时，要求统一输出为升/小时且不允许取整；该边换算后为1升/小时（整数），但按当前求解器校验规则，不能预先假定原值换算后一定满足整数容量要求。若程序校验发现换算后容量不是非负整数，则超出最大流仅支持非负整数容量的范围。
- flow_unknown_conversion #1：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- flow_reverse_conversion #2：failed unsupported 当前求解器要求最大流容量在统一输出单位下为非负整数；原边容量0.001立方米/小时换算为升/小时等于1升/小时，但原题禁止改变统一输出单位或取整，因此无法按指定单位校验并求解。
- flow_unknown_conversion #2：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- graph_units_fractional_flow #3：local_guard  换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。
- flow_reverse_conversion #3：failed unsupported 原边容量为0.001立方米/小时，统一输出单位升/小时后为1升/小时（整数），但当前求解器要求输出单位下的容量换算为整数；该题指定输出单位为升/小时且禁止取整。若仅按原单位求解，可支持；但明确要求按升/小时输出时超出当前求解器对统一输出单位下整数容量的限制。
- flow_unknown_conversion #3：local_guard  图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。

7开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。

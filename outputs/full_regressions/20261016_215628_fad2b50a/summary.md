# 当前版本完整开发回归

完成89/89；原始通过82；格式修复后累计通过82；本地处理后最终通过87。
路径计数：{'native': 82, 'local_guard': 5, 'failed': 2}。
原schema通过89；schema未知0。
已知tokens 387912；usage未知0。
本地CSV检查7/7，API调用0，单独统计。

原始通过=无需格式修复或本地纠错追问，且原题评分通过；正常单位转换与数值求解属于正常流程，不计修复。格式修复后累计通过=原始通过+仅靠允许的格式删除恢复的通过。含本地处理最终通过还包含原文引用修复及本地拦截处理。schema通过本身不代表题意正确。

| 类型 | 数量 | 原始通过 | 格式修复后累计 | 本地处理后最终 |
|---|---:|---:|---:|---:|
| original | 8 | 8 | 8 | 8 |
| paraphrase | 8 | 7 | 7 | 7 |
| missing | 8 | 8 | 8 | 8 |
| error | 8 | 7 | 7 | 8 |
| units | 3 | 3 | 3 | 3 |
| boundary | 12 | 12 | 12 | 12 |
| immutable | 14 | 12 | 12 | 13 |
| conflict | 12 | 12 | 12 | 12 |
| equivalent | 9 | 8 | 8 | 9 |
| graph_units | 7 | 5 | 5 | 7 |

## 失败与本地接管

- DYN02_error：local_guard，；环境容量K=0.0不满足K>0。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。
- NET02_paraphrase：failed，needs_clarification；图边原值或单位引用不在原题中，请核对原始记录。
- immutable_lock_keep：local_guard，；环境容量K=0.0不满足K>0。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。
- immutable_permission：failed，unsupported；Logistic 模型要求环境容量 K 为正实数；原题给出环境容量恒定 0 个，K<=0 会使当前模型无效（K=0 时 dN/dt=rN(1-N/K) 除零）。按题目要求不自行替换数值，因此当前参数下不支持该连续 Logistic 模型。
- equivalent_exponent_difference：local_guard，；环境容量K的原文记录相互冲突：“环境容量恒定5e-1个”；“K=6e-1个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- graph_units_unknown：local_guard，；图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。
- graph_units_fractional_flow：local_guard，；换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。

固定89个在线场景，每题1次，不重试、不在中途调参。全部同义表达、单位与边界场景均为开发变体，不算新基础题。仅为单轮开发回归，不用于稳定率或保留题泛化结论。关键词追问与严格结构评分仍需定性复核；任何后续审查单独保存，不覆盖本统计。

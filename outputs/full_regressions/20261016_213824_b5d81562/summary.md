# 当前版本完整开发回归

完成82/82；原始通过76；格式修复后累计通过76；本地处理后最终通过81。
路径计数：{'native': 76, 'failed': 1, 'local_guard': 5}。
原schema通过82；schema未知0。
已知tokens 323921；usage未知0。
本地CSV检查7/7，API调用0，单独统计。

原始通过=无需格式修复或本地纠错追问，且原题评分通过；正常单位转换与数值求解属于正常流程，不计修复。格式修复后累计通过=原始通过+仅靠允许的格式删除恢复的通过。含本地处理最终通过还包含原文引用修复及本地拦截处理。schema通过本身不代表题意正确。

| 类型 | 数量 | 原始通过 | 格式修复后累计 | 本地处理后最终 |
|---|---:|---:|---:|---:|
| original | 8 | 8 | 8 | 8 |
| paraphrase | 8 | 8 | 8 | 8 |
| missing | 8 | 8 | 8 | 8 |
| error | 8 | 8 | 8 | 8 |
| units | 3 | 2 | 2 | 2 |
| boundary | 12 | 12 | 12 | 12 |
| immutable | 14 | 11 | 11 | 14 |
| conflict | 12 | 10 | 10 | 12 |
| equivalent | 9 | 9 | 9 | 9 |

## 失败与本地接管

- path_units：failed，evaluation_failed；{"passed": false, "checks": {"original_edges": false, "source_target": true, "path": true, "distance": false}}
- immutable_lock_original：local_guard，；环境容量K=0.0不满足K>0。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。
- immutable_lock_dont：local_guard，；环境容量K=0.0不满足K>0。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。
- immutable_lock_keep：local_guard，；环境容量K=0.0不满足K>0。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。
- conflict_zero_positive：local_guard，；环境容量K的原文记录相互冲突：“环境容量恒定0个”；“环境容量为0.5个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。
- conflict_all_negative：local_guard，；环境容量K的原文记录相互冲突：“容量恒定-1个”；“K=-2个”。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。

固定82个在线场景，每题1次，不重试、不在中途调参。全部同义表达、单位与边界场景均为开发变体，不算新基础题。仅为单轮开发回归，不用于稳定率或保留题泛化结论。关键词追问与严格结构评分仍需定性复核；任何后续审查单独保存，不覆盖本统计。

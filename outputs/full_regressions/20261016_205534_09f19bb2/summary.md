# 当前版本完整开发回归

完成47/47；原始通过46；格式修复后累计通过46；含护栏最终通过46。
路径计数：{'native': 46, 'failed': 1}。
原schema通过47；schema未知0。
已知tokens 171478；usage未知0。
本地CSV检查7/7，API调用0，单独统计。

原始通过=无需格式修复或本地纠错追问，且原题评分通过；正常单位转换与数值求解属于正常流程，不计修复。格式修复后累计通过=原始通过+仅靠允许的格式删除恢复的通过。含护栏最终通过还包含本地拦截并正确追问。schema通过本身不代表题意正确。

| 类型 | 数量 | 原始通过 | 格式修复后累计 | 含护栏最终 |
|---|---:|---:|---:|---:|
| original | 8 | 8 | 8 | 8 |
| paraphrase | 8 | 8 | 8 | 8 |
| missing | 8 | 8 | 8 | 8 |
| error | 8 | 7 | 7 | 7 |
| units | 3 | 3 | 3 | 3 |
| boundary | 12 | 12 | 12 | 12 |

## 失败与本地接管

- DYN02_error：failed，clarification_semantics；{"applied": true, "passed": false, "checks": {"expected_status": true, "nonempty_question": true, "relevant_topic": true, "no_replacement_suggestion": false}, "text": "请提供正实数环境容量K（可为小数）。", "scope": "状态/主题初筛；显式禁止改值时检查修改建议，否则Logistic容量检查正实数限制。不是完整语义证明。"}

固定47个在线场景，每题1次，不重试、不在中途调参。24变体、3个单位场景与12个边界场景不算新基础题。仅为单轮开发回归，不用于稳定率或保留题泛化结论。关键词追问与严格结构评分仍需定性复核；任何后续审查单独保存，不覆盖本统计。

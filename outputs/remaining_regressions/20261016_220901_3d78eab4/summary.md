# 图引用与修改许可定向回归

完成36/36；原始35；格式后累计35；本地后累计35。
路径计数：{'native': 35, 'failed': 1}。
tokens 163539；usage未知0；对照误接管0。

| 场景 | 完成次数 | 原始 | 格式后累计 | 本地后累计 |
|---|---:|---:|---:|---:|
| graph_previous | 3 | 3 | 3 | 3 |
| graph_global_before | 3 | 3 | 3 | 3 |
| graph_inline | 3 | 3 | 3 | 3 |
| graph_path_units | 3 | 3 | 3 | 3 |
| graph_mixed_flow | 3 | 3 | 3 | 3 |
| permission_previous | 3 | 3 | 3 | 3 |
| permission_paraphrase | 3 | 3 | 3 | 3 |
| permission_valid | 3 | 3 | 3 | 3 |
| permission_forbidden | 3 | 3 | 3 | 3 |
| permission_missing | 3 | 2 | 2 | 2 |
| permission_conflict | 3 | 3 | 3 | 3 |
| permission_threshold | 3 | 3 | 3 | 3 |

每场景3次、无重试、批次中不改代码；开发变体不代表独立题族或稳定率。正常换算不算修复；引用修复计local_source_repair；响应接管计local_guard；三层为累计口径，不可相加。

## 非原始通过记录
- permission_missing #1：failed response_semantics {"passed": false, "checks": {"expected_status": true, "clarification": true, "capacity": true, "positive_real": false, "fraction_allowed": false, "no_integer_requirement": true}, "scope": "预先固定的部分语义检查，仍需定性复核"}

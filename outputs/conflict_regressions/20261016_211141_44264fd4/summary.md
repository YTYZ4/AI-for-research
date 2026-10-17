# 容量冲突优先澄清重复评测

原始通过27/30；格式修复后累计27/30；含本地处理最终30/30。
容量冲突策略误拦截0；策略接管0。
tokens 110108；usage未知0。

| 场景 | 通过次数 |
|---|---:|
| zero_positive | 3/3 |
| two_positive | 3/3 |
| reverse | 3/3 |
| three_values | 3/3 |
| same_positive | 3/3 |
| same_invalid | 3/3 |
| corrected | 3/3 |
| missing | 3/3 |
| valid_above | 3/3 |
| previous_failure | 3/3 |

原始通过不含格式修复或本地接管。有效输入不必要追问仍判失败，不能与本地误拦截混淆。每场景3次开发测试不证明长期稳定；原始回答和失败不重试覆盖。

# 容量数值等价写法重复评测

原始通过27/30；格式修复后累计27/30；含本地处理最终28/30。
容量冲突策略误拦截0；策略接管1。
tokens 124029；usage未知0。

| 场景 | 通过次数 |
|---|---:|
| trailing_zero | 3/3 |
| leading_dot | 2/3 |
| signed | 3/3 |
| scientific | 3/3 |
| integer | 3/3 |
| same_invalid | 2/3 |
| near_difference | 3/3 |
| exponent_difference | 3/3 |
| missing_rate | 3/3 |
| corrected | 3/3 |

原始通过不含格式修复或本地接管。有效输入不必要追问仍判失败，不能与本地误拦截混淆。每场景3次开发测试不证明长期稳定；原始回答和失败不重试覆盖。

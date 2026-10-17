# 开发变体两次重复评测

完成64/64；通过62/64；已知tokens 167277；未知usage 0。
固定题面/规则，不重试、不修复。两次是两个独立请求；API默认采样，无独立性或长期稳定性保证。

| 类型 | 通过 | 总数 |
|---|---:|---:|
| original | 16 | 16 |
| paraphrase | 16 | 16 |
| missing | 16 | 16 |
| error | 14 | 16 |

## 两次一致性

{'both_pass': 31, 'both_fail': 1}

mixed表示同题一次通过一次失败；both_fail表示重复出现的缺陷，不代表稳定正确。仅比较验收结果，措辞差异或不同等价最优解不算失败。

## 自动判定失败

- DYN02_error / 第1次：generation_error；ValueError: Logistic 初值须非负、环境容量须为正
- DYN02_error / 第2次：generation_error；ValueError: Logistic 初值须非负、环境容量须为正

预期追问只按状态和关键词初筛，仍须审查问题是否相关且未擅自补值。结构评分可能拒绝等价重写；评分器异常单列，不算模型错误。全部属于开发题变体，不计新增基础题或保留测试。

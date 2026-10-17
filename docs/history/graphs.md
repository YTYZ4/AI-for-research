# 第四类能力：图与网络首轮验收

2026-10-16，版本0.6.0。新增 NET01 最短路径与 NET02 最大流，沿用同一自然语言 CLI、受限JSON模型、独立本地算法、运行记录和中文报告。无需新增依赖。

## 交付与验证

- 最短路径输出路径、距离标签和可达集合；断连时明确不可达。
- 最大流输出逐边容量/流量、守恒检查和最小割，流与割相等作为最优性证据。
- 新增 edges.csv、人工参考规格、任务卡及原题独立评分器。
- 55项自动测试通过，包含既有优化/拟合/动态流程，以及各30个小型随机图的简单路径或源汇割穷举对照；这些是程序验证，不是大模型试验题数。

真实调用：最短路线S→B→A→C→T为8千米；最大流15立方米/小时，最小割容量15。两题原始参数和解均经 evaluation/graphs.py 独立复算通过。该评分器不读取运行时生成图作为参考图，允许替代最优流方案。

## 真实调用和失败保留

| 场景 | 状态 | tokens |
|---|---|---:|
| shortest_path | optimal | 2533 |
| max_flow | optimal | 2526 |
| unreachable | needs_clarification | 2350 |
| missing_capacity | needs_clarification | 2374 |
| unreachable_fixed | unreachable | 2498 |

合计 12281 tokens，实际金额以服务商账单为准。首次不可达例被模型错误地要求补路：原题已经声明没有其他边，此时不是信息缺失。该失败记录完整保留。补充“完整断连图仍须ready、不得要求补边”的指令后，对相同原题重试，得到unreachable，原图核对通过。缺少已存在管道容量时正确触发追问；初次追问附带“容量不限”的建议不符合当前能力边界，提示词也已收紧为有限整数容量，未将这一点宣称为额外线上验收通过。

以上是开发回归，不是固定协议成功率实验；提示修改后的结果不能覆盖修改前失败。

证据：

- `outputs/modeling_assistant/development_v060/shortest_path/20261016_161638_bc850bdd`
- `outputs/modeling_assistant/development_v060/max_flow/20261016_161638_882d5bb1`
- `outputs/modeling_assistant/development_v060/unreachable/20261016_161729_7e75a698`
- `outputs/modeling_assistant/development_v060/missing_capacity/20261016_161729_12b9333d`
- `outputs/modeling_assistant/development_v060/unreachable_fixed/20261016_162030_b5fb7488`

## 项目状态与下一步

四类、八个开发题已有初始端到端流程，具体能力边界见各任务卡。20题完整题库、12个保留题冻结、完整目标范围适配、三组对照实验、自动反馈修复和外部试用仍未完成。不能由开发例题成功推出跨题型泛化已验证。

下一步优先统一批量实验入口与评分汇总，固定输入、模型版本、重复次数、预算、错误分类及原始响应；先在开发集跑通，再冻结保留题与评价协议。八周时间表不因提前接通原型而视为已完成研究。

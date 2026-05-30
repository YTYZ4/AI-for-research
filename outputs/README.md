# outputs

本目录存放实验运行后生成的图像、CSV、JSON、评估摘要和可视化结果。

它回答的是：“某次运行实际产出了什么？”

它不存放源代码、prompt、模型原始回复或 failure-case 参考材料。那些分别放在 `solutions/`、`prompts/`、`runs/` 和 `metrics/`。

## Layout

| path | purpose |
|---|---|
| `hw1_op1/` | A1 Seam Carving 的输出图、对比图和 runtime metrics |
| `hw2_op2/` | A2 RSLT inpainting 的恢复图、对比图和 `eval_summary.json` |

## Naming Rule

按 run 保存的输出目录应尽量和 `runs/`、`metrics/` 中的 `run_id` 对齐，例如：

- `outputs/hw1_op1/run_006_direct_answer/`
- `outputs/hw2_op2/run_030_direct_answer/`

这样可以从一条 run 文档一路追到对应代码、指标和输出。

## Cleanup Rule

- 可删除：明显的临时目录、空目录、`.DS_Store`、未被 run/metrics/report 引用的试跑垃圾。
- 谨慎删除：带正式 `run_###` 名称的目录，它们通常是 `runs/` 和 `metrics/` 的证据来源。
- 不要放入：源代码、模型回复、prompt 模板、题目要求。


# solutions

本目录存放研究用的代码产物、参考实现、模型生成版本和 failure cases。

它回答的是：“某个任务的代码/解法在哪里？”

它不存放运行输出图、评估结果图或临时可视化。那些统一放在顶层 `outputs/`。

## Layout

| path | purpose |
|---|---|
| `hw1_op1/` | A1 Seam Carving 的参考实现、模型生成实现和 failure cases |
| `hw2_op2/` | A2 RSLT inpainting 的模型生成实现、failure cases 和 benchmark 脚本 |

## Common Subdirectories

| name | purpose |
|---|---|
| `gold/` | 人工整理或稳定版本的参考实现 |
| `reference_template/` | 早期模板或题目原始模板 |
| `src/` | 当前手工整理的可运行入口 |
| `generated/` | 按 run 保存的模型生成代码、prompt 和原始回复 |
| `failure_cases/` | curated bug、症状说明、诊断和修复参考 |
| `figs/` | 任务自带或说明用素材，不是实验运行输出 |

## A2 Boundary

A2 的主工程在顶层 `hw2-op2/`。其中 `hw2-op2/src/chapter5_rslt.py` 是 A2 主案例的 gold reference。

`solutions/hw2_op2/` 只保存研究过程中围绕 A2 生成、修补和评测的产物，不复制整个 A2 工程。

## Output Rule

不要在 `solutions/` 下新建 `outputs/`。如果脚本生成图片、CSV、JSON 或评估摘要，请写入：

- `outputs/hw1_op1/<run_id_or_case>/`
- `outputs/hw2_op2/<run_id_or_case>/`


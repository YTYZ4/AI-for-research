# AI-for-research

本仓库记录一个大研课题：研究大模型在数学建模与求解教学中的使用方式。

我目前关注的不是“模型能不能直接给答案”，而是把模型生成过程整理成可检查、可复现、可评分的教学流程：

- 题目要求先结构化
- 代码和输出必须能落盘
- 每次运行都有 run 文档和 metrics 行
- 固定错误要能诊断、修补、回归验证
- 最后沉淀成题库、模板和小样本试用材料

## 当前进度

截至中期阶段，主案例已经闭环，正式受试者数据还没有开始采集。

| 模块 | 状态 | 主要证据 |
|---|---|---|
| A1 Seam Carving | 已完成主案例闭环 | 12 条 guidance 记录、18 条性能记录、9 条 bug-repair 记录 |
| A2 低秩图像修复 | 已完成主案例闭环 | 15 条 guidance 记录、60 条恢复结果、9 条 bug-repair 记录、48 条 expanded-scope 记录 |
| 题库 | 中期版已成型 | 16 个正式条目，按主案例、固定协议、failure case 三层整理 |
| A3 / A4 | 首发条目已冻结 | 已有 requirement 和 taskcard，还未进入正式实验 |
| CLI 原型 | 可演示 | `run_research_case.py --demo advisor` |
| 小样本试用 | 材料已准备 | 已完成 1 次内部 dry run，4 人 formal pilot 尚未采集 |
| 中期汇报 | 已整理 | [report/中期汇报.pptx](report/中期汇报.pptx) |

## 当前结论

现在比较稳的结论有两条：

1. 在 A1 / A2 的固定协议下，结构化指导更明显的价值是让过程更可查，包括自检覆盖、根因说明和回归说明。
2. 在 A2 这类固定图像修复任务上，三种提示方式的最终恢复指标基本一致，所以不能把结论写成“结构化指导显著提高图像质量”。

换句话说，目前证据支持的是“过程质量和可复查性提升”，不是“大样本教学效果已经被证明”。

## 任务线索

### A1：Seam Carving

A1 用接缝裁剪任务验证代码生成、固定协议复现和 bug repair。

常用入口：

- 任务卡：[task_cards/A1_seam_carving_taskcard_v1.md](task_cards/A1_seam_carving_taskcard_v1.md)
- 评测协议：[report/a1_eval_protocol_v0.md](report/a1_eval_protocol_v0.md)
- 阶段总结：[report/a1_v1_stage_summary.md](report/a1_v1_stage_summary.md)
- bug repair 总结：[report/a1_bug_repair_summary_v0.md](report/a1_bug_repair_summary_v0.md)
- 指标表：[metrics/a1_guidance_eval_v0.csv](metrics/a1_guidance_eval_v0.csv), [metrics/a1_codegen_perf_v0.csv](metrics/a1_codegen_perf_v0.csv), [metrics/a1_failure_repair_eval_v0.csv](metrics/a1_failure_repair_eval_v0.csv)

### A2：低秩图像修复

A2 从早期较宽的“SVD 图像压缩”方向，收束为低秩图像任务族下的灰度图像修复主案例：

`hw2-op2/src/chapter5_rslt.py::rslt_inpainting(...)`

常用入口：

- 任务要求：[problems/a2_requirement.md](problems/a2_requirement.md)
- 任务卡：[task_cards/A2_rslt_inpainting_taskcard_v1.md](task_cards/A2_rslt_inpainting_taskcard_v1.md)
- 评测协议：[report/a2_eval_protocol_v0.md](report/a2_eval_protocol_v0.md)
- 复现实验总结：[report/a2_replication_summary_v0.md](report/a2_replication_summary_v0.md)
- expanded-scope 总结：[report/a2_expanded_scope_summary_v0.md](report/a2_expanded_scope_summary_v0.md)
- bug repair 总结：[report/a2_bug_repair_summary_v0.md](report/a2_bug_repair_summary_v0.md)
- 指标表：[metrics/a2_guidance_eval_v0.csv](metrics/a2_guidance_eval_v0.csv), [metrics/a2_recovery_perf_v0.csv](metrics/a2_recovery_perf_v0.csv), [metrics/a2_failure_repair_eval_v0.csv](metrics/a2_failure_repair_eval_v0.csv)

### A3 / A4：后续扩展

A3 / A4 目前只作为扩展入口，不支撑主结论。

- A3 曲线拟合：[problems/a3_requirement.md](problems/a3_requirement.md), [task_cards/A3_taskcard_v1.md](task_cards/A3_taskcard_v1.md)
- A4 Poisson 图像融合：[problems/a4_requirement.md](problems/a4_requirement.md), [task_cards/A4_taskcard_v1.md](task_cards/A4_taskcard_v1.md)

## 中期材料

如果只想快速了解当前阶段，建议按这个顺序看：

1. [report/中期汇报.pptx](report/中期汇报.pptx)
2. [report/phase2_progress_report_2026-04-12.md](report/phase2_progress_report_2026-04-12.md)
3. [report/task_bank_index_v1.md](report/task_bank_index_v1.md)
4. [report/small_sample_pilot_plan_v0.md](report/small_sample_pilot_plan_v0.md)
5. [report/pilot_internal_dry_run_result_2026-04-20.md](report/pilot_internal_dry_run_result_2026-04-20.md)

## CLI 原型

当前有一个最小命令行入口，用来串起题目、任务卡、prompt、run 文档和 metrics 摘要。

```bash
python run_research_case.py --list
python run_research_case.py --demo advisor
python run_research_case.py --case A1 --mode plain_guidance --track baseline
python run_research_case.py --case A2 --mode coe_guided --track bug-repair
python run_research_case.py --case A2 --mode direct_answer --track expanded-scope
```

说明文档：[report/prototype_cli_v0.md](report/prototype_cli_v0.md)

## 仓库结构

| 路径 | 内容 |
|---|---|
| `task_cards/` | 任务卡和 bug-repair task card |
| `problems/` | 题目要求 |
| `prompts/` | direct / plain guidance / CoE 提示词 |
| `runs/` | 每次实验的运行记录 |
| `metrics/` | 结构化指标表和 codebook |
| `report/` | 协议、总结、中期材料、pilot 方案 |
| `pilot/` | 小样本试用表单、评分表和任务包 |
| `solutions/` | gold / generated / failure case 代码 |
| `outputs/` | 图像输出和实验结果 |
| `hw2-op2/` | A2 低秩图像修复项目本体 |

## 复现入口

A1 复现：

```bash
python solutions/hw1_op1/src/run_step6_comparisons.py
python solutions/hw1_op1/generated/run_015_plain_guidance_rep3/src/run_protocol_eval.py
```

A2 项目：

```bash
cd hw2-op2
python run_all.py
python gui.py
```

依赖以各目录中的 `requirements.txt` / `environment.yml` 为准。当前主实验使用 conda 环境 `llmft`。

## 下一步

短期先做三件事：

1. 跑完 S01-S04 四个 formal pilot session。
2. 每个 session 结束后立刻回填 participant form、session record、scoring sheet 和 CSV。
3. 根据首轮反馈修订模板字段和评分口径。

中期之后再推进：

- A3 / A4 的固定协议和 failure case
- 更完整的 CLI / Notebook 展示入口
- 更大范围的学生试用和对照数据

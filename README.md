# AI-for-research

本仓库记录一个大研课题：研究大模型在数学建模与求解教学中的使用方式。

项目关注点不是“模型能不能直接给答案”，而是把模型生成过程整理成可检查、可复现、可评分、可教学复用的流程：

- 题目要求先结构化
- prompt、代码、输出和评分口径分开保存
- 每次运行都有 run 文档和 metrics 行
- 固定错误能诊断、修补、回归验证
- 最后沉淀成题库、模板、原型入口和小样本试用材料

## 当前阶段

截至当前仓库材料，A1 / A2 首轮主案例已经闭环；中期阶段的主要成果是把零散实验收束成可复查的证据链、题库索引、模板库、CLI 原型和 pilot 准备材料。

| 模块 | 当前状态 | 主要证据 |
|---|---|---|
| A1 Seam Carving | 已完成主案例闭环 | 12 条 guidance 记录、18 条性能记录、9 条 bug-repair 记录 |
| A2 低秩图像修复 | 已完成主案例闭环 | 15 条 guidance 记录、60 条恢复结果、9 条 bug-repair 记录、48 条 expanded-scope case 记录 |
| 题库 | 中期版已成型 | 16 个正式条目，按主案例、固定协议、expanded-scope 代表案例和 failure cases 分层 |
| A3 / A4 | 首发条目已冻结 | 已有 requirement 和 taskcard，尚未进入固定协议实验 |
| CLI 原型 | 可演示 | `run_research_case.py --demo advisor` |
| 小样本试用 | 材料已准备 | 已完成 1 次内部 dry run；4 个 formal pilot task pack 已预建，正式受试者数据尚未采集 |
| 中期汇报 | 已整理 | [大研中期汇报.pptx](大研中期汇报.pptx) |

## 稳定结论

当前证据最稳妥支持两点：

1. 在 A1 / A2 的固定协议下，`plain_guidance` / `coe_guided` 的主要价值是提高过程可复查性，包括自检覆盖、根因说明和回归说明。
2. 在 A2 这类冻结协议的图像修复任务上，三种提示方式的最终恢复指标基本一致，因此不应写成“结构化 guidance 显著提高图像质量”。

换句话说，当前结论是“过程质量和可解释性提升”，不是“大样本教学效果已经被证明”。

## 证据链

一条完整实验记录大致按下面的链路组织：

```text
problems/ 或 task_cards/
  -> prompts/
  -> solutions/<case>/generated/<run>/
  -> outputs/<case>/<run>/
  -> metrics/*.csv
  -> runs/*.md
  -> report/*.md
```

其中：

- `solutions/` 保存代码产物、参考实现、模型生成版本和 failure cases。
- `outputs/` 保存运行后生成的图片、CSV、JSON 和评估摘要。
- `metrics/` 保存结构化评分表和 codebook。
- `runs/` 保存每次实验的叙事记录。
- `report/` 保存阶段总结、协议、题库索引、pilot 方案和中期收口材料。

## 任务主线

### A1: Seam Carving

A1 用接缝裁剪任务验证代码生成、固定协议复现和 bug repair。

常用入口：

- 任务要求：[problems/hw1_op1_requirement.md](problems/hw1_op1_requirement.md)
- 主任务卡：[task_cards/A1_seam_carving_taskcard_v1.md](task_cards/A1_seam_carving_taskcard_v1.md)
- bug-repair 任务卡：[task_cards/A1_bug_repair_taskcard_v0.md](task_cards/A1_bug_repair_taskcard_v0.md)
- 评测协议：[report/a1_eval_protocol_v0.md](report/a1_eval_protocol_v0.md)
- 阶段总结：[report/a1_v1_stage_summary.md](report/a1_v1_stage_summary.md)
- bug-repair 总结：[report/a1_bug_repair_summary_v0.md](report/a1_bug_repair_summary_v0.md)
- 指标表：[metrics/a1_guidance_eval_v0.csv](metrics/a1_guidance_eval_v0.csv), [metrics/a1_codegen_perf_v0.csv](metrics/a1_codegen_perf_v0.csv), [metrics/a1_failure_repair_eval_v0.csv](metrics/a1_failure_repair_eval_v0.csv)

### A2: 低秩图像修复

A2 从早期较宽的“SVD 图像压缩”方向，收束为低秩图像任务族下的灰度图像修复主案例：

`hw2-op2/src/chapter5_rslt.py::rslt_inpainting(...)`

常用入口：

- 任务要求：[problems/a2_requirement.md](problems/a2_requirement.md)
- 主任务卡：[task_cards/A2_rslt_inpainting_taskcard_v1.md](task_cards/A2_rslt_inpainting_taskcard_v1.md)
- bug-repair 任务卡：[task_cards/A2_bug_repair_taskcard_v0.md](task_cards/A2_bug_repair_taskcard_v0.md)
- 评测协议：[report/a2_eval_protocol_v0.md](report/a2_eval_protocol_v0.md)
- 复现实验总结：[report/a2_replication_summary_v0.md](report/a2_replication_summary_v0.md)
- expanded-scope 总结：[report/a2_expanded_scope_summary_v0.md](report/a2_expanded_scope_summary_v0.md)
- bug-repair 总结：[report/a2_bug_repair_summary_v0.md](report/a2_bug_repair_summary_v0.md)
- A2 工程说明：[hw2-op2/README.md](hw2-op2/README.md)
- 指标表：[metrics/a2_guidance_eval_v0.csv](metrics/a2_guidance_eval_v0.csv), [metrics/a2_recovery_perf_v0.csv](metrics/a2_recovery_perf_v0.csv), [metrics/a2_failure_repair_eval_v0.csv](metrics/a2_failure_repair_eval_v0.csv), [metrics/a2_expanded_scope_perf_v0.csv](metrics/a2_expanded_scope_perf_v0.csv)

### A3 / A4

A3 / A4 目前作为后续扩展入口，不支撑当前主结论。

- A3 曲线拟合：[problems/a3_requirement.md](problems/a3_requirement.md), [task_cards/A3_taskcard_v1.md](task_cards/A3_taskcard_v1.md)
- A4 Poisson 图像融合：[problems/a4_requirement.md](problems/a4_requirement.md), [task_cards/A4_taskcard_v1.md](task_cards/A4_taskcard_v1.md)

## 题库口径

当前中期题库按“主案例家族 / 固定协议与子任务 / failure cases”三层整理。

正式计入中期题库的条目共 16 个：

- A1：2 个主任务 + 3 个 failure cases
- A2：2 个 fixed protocol + 4 个 expanded-scope 代表案例 + 3 个 failure cases
- A3：1 个首发条目
- A4：1 个首发条目

注意：direct / plain guidance / CoE 的重复 rerun 是证据材料，不直接当成额外题库条目。

详见 [report/task_bank_index_v1.md](report/task_bank_index_v1.md) 和 [report/task_bank_status_v1.md](report/task_bank_status_v1.md)。

## Metrics 概览

| 文件 | 数据行数 | 用途 |
|---|---:|---|
| [metrics/a1_guidance_eval_v0.csv](metrics/a1_guidance_eval_v0.csv) | 12 | A1 prompt 模式下的 artifact / runnable / correct / self-check 评价 |
| [metrics/a1_codegen_perf_v0.csv](metrics/a1_codegen_perf_v0.csv) | 18 | A1 代码生成运行时间和输出状态 |
| [metrics/a1_failure_repair_eval_v0.csv](metrics/a1_failure_repair_eval_v0.csv) | 9 | A1 failure-case 修复评分 |
| [metrics/a2_guidance_eval_v0.csv](metrics/a2_guidance_eval_v0.csv) | 15 | A2 prompt 模式下的 artifact / runnable / correct / self-check 评价 |
| [metrics/a2_recovery_perf_v0.csv](metrics/a2_recovery_perf_v0.csv) | 60 | A2 fixed protocol 的 PSNR / SSIM / RSE / runtime |
| [metrics/a2_failure_repair_eval_v0.csv](metrics/a2_failure_repair_eval_v0.csv) | 9 | A2 failure-case 修复评分 |
| [metrics/a2_expanded_scope_eval_v0.csv](metrics/a2_expanded_scope_eval_v0.csv) | 3 | A2 expanded-scope 主记录 |
| [metrics/a2_expanded_scope_perf_v0.csv](metrics/a2_expanded_scope_perf_v0.csv) | 48 | A2 expanded-scope case 级恢复指标 |
| [metrics/pilot_session_log_dry_run_v0.csv](metrics/pilot_session_log_dry_run_v0.csv) | 1 | 内部 dry run 的 session 级记录 |
| [metrics/pilot_session_log_template_v0.csv](metrics/pilot_session_log_template_v0.csv) | 0 | formal pilot 待回填模板 |

每个 CSV 的字段含义以同目录下的 `*_codebook_v0.md` 为准。

## Pilot 状态

小样本试用当前定位是 feasibility-style pilot：先观察 baseline workflow 与 process-guided workflow 在过程记录、自检覆盖、根因说明、回归说明和主观清晰度上的差异。

当前已完成：

- `2026-04-20` 内部 dry run：见 [report/pilot_internal_dry_run_result_2026-04-20.md](report/pilot_internal_dry_run_result_2026-04-20.md)
- dry run 记录：[pilot/dry_run_records/PILOT_20260420_000/](pilot/dry_run_records/PILOT_20260420_000/)
- 首轮 4 个 formal pilot task pack：[pilot/formal_pilot_task_packs/](pilot/formal_pilot_task_packs/)
- session log 模板：[metrics/pilot_session_log_template_v0.csv](metrics/pilot_session_log_template_v0.csv)

正式受试者数据尚未采集。首轮计划是：

- S01：`T2_A1_bug_01` + `baseline_workflow`
- S02：`T2_A1_bug_01` + `process_guided_workflow`
- S03：`T3_A2_bug_01` + `baseline_workflow`
- S04：`T3_A2_bug_01` + `process_guided_workflow`

详见 [report/small_sample_pilot_plan_v0.md](report/small_sample_pilot_plan_v0.md)、[report/pilot_round1_schedule_v0.md](report/pilot_round1_schedule_v0.md) 和 [pilot/formal_pilot_task_packs/README.md](pilot/formal_pilot_task_packs/README.md)。

## 快速阅读顺序

如果只想快速理解当前项目，建议按这个顺序看：

1. [大研中期汇报.pptx](大研中期汇报.pptx)
2. [report/midterm_stage_summary_v0.md](report/midterm_stage_summary_v0.md)
3. [report/phase2_progress_report_2026-04-12.md](report/phase2_progress_report_2026-04-12.md)
4. [report/task_bank_index_v1.md](report/task_bank_index_v1.md)
5. [report/small_sample_pilot_plan_v0.md](report/small_sample_pilot_plan_v0.md)
6. [report/pilot_internal_dry_run_result_2026-04-20.md](report/pilot_internal_dry_run_result_2026-04-20.md)

早期规划和参考附件集中放在 [Other/](Other/)：

- [Other/TimeLine.docx](Other/TimeLine.docx)
- [Other/talktoai.pdf](Other/talktoai.pdf)
- [Other/大研课题规划建议.pdf](Other/大研课题规划建议.pdf)
- [Other/中期研究小白讲透版.pdf](Other/中期研究小白讲透版.pdf)

## CLI 原型

当前有一个最小命令行入口，用来串起题目、任务卡、prompt、run 文档和 metrics 摘要。

```bash
python3 run_research_case.py --list
python3 run_research_case.py --demo advisor
python3 run_research_case.py --case A1 --mode plain_guidance --track baseline
python3 run_research_case.py --case A2 --mode coe_guided --track bug-repair
python3 run_research_case.py --case A2 --mode direct_answer --track expanded-scope
python3 run_research_case.py --case A2 --mode plain_guidance --track fresh-generation
```

说明文档：[report/prototype_cli_v0.md](report/prototype_cli_v0.md) 和 [report/advisor_demo_entry_v1.md](report/advisor_demo_entry_v1.md)。

## 仓库结构

| 路径 | 内容 |
|---|---|
| [problems/](problems/) | 原始题目要求和 A2/A3/A4 requirement |
| [task_cards/](task_cards/) | 主任务卡和 bug-repair task card |
| [prompts/](prompts/) | A1 / A2 的 direct_answer、plain_guidance、CoE prompt |
| [runs/](runs/) | 每次实验的运行记录，共 66 份 run / queue / template 文档 |
| [metrics/](metrics/) | 结构化指标表和 codebook |
| [report/](report/) | 协议、阶段总结、中期材料、题库、pilot 方案 |
| [pilot/](pilot/) | 小样本试用表单、评分表、dry run 记录和 formal task packs |
| [solutions/](solutions/) | A1 / A2 的参考实现、模型生成代码和 failure cases；不放运行输出 |
| [outputs/](outputs/) | A1 / A2 每次运行生成的图片、CSV、JSON 和评估摘要；不放源代码 |
| [hw2-op2/](hw2-op2/) | A2 低秩图像修复项目本体，`src/chapter5_rslt.py` 是 A2 主案例 gold reference |
| [Other/](Other/) | 早期规划、导师沟通材料和辅助说明附件 |

`solutions/`、`outputs/`、`hw2-op2/` 各自有目录 README，新增文件优先按这些入口说明归档。

## 复现入口

A1 复现：

```bash
python3 solutions/hw1_op1/src/run_step6_comparisons.py
python3 solutions/hw1_op1/generated/run_015_plain_guidance_rep3/src/run_protocol_eval.py
```

A2 项目：

```bash
cd hw2-op2
python3 run_all.py
python3 gui.py
```

依赖以各目录中的 `requirements.txt` / `environment.yml` 为准。当前主实验记录中使用的 conda 环境名是 `llmft`。

## 下一步

短期优先：

1. 跑完 S01-S04 四个 formal pilot session。
2. 每个 session 结束后回填 participant form、session record、scoring sheet 和 CSV。
3. 根据首轮反馈修订模板字段、评分口径和 task pack。

中期之后再推进：

- A3 / A4 的固定协议和 failure cases
- 更完整的 CLI / Notebook 展示入口
- 更大范围的学生试用和对照数据


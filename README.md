# AI-for-research
一句话目标：用 A1/A2 主案例做“过程化指导 + 结构化检查 + 纠错评估”的研究仓库。

一句话阶段判断：A1 / A2 首轮主案例闭环已完成；当前中期重点是收束模板库、检查清单、错误分类、题库页和原型入口。

## 当前状态
- A1 v1 已收尾：`direct_answer` / `plain_guidance` / `coe_guided` 主实验、固定协议复现、bug-repair benchmark 均已完成。
- A1 failure cases 已从复查资产扩展为 9 条可评分的 bug-repair benchmark 记录。
- A2 当前统一表述为：低秩图像任务族下，已完成范围收束并完成主案例闭环的 `hw2-op2/src/chapter5_rslt.py::rslt_inpainting(...)` 灰度图像修复主案例。
- A2 的 baseline、fixed-protocol replication、bug-repair benchmark、expanded-scope validation、fresh-generation replication 均已完成。
- A2 当前已形成 15 条 guidance 主记录、60 条恢复结果记录、9 条 bug-repair 记录，以及 48 条 expanded-scope case 记录。
- 正式 task-bank 页面已建立，当前按“主案例家族 / 固定协议子任务 / failure cases”三层整理出 `16` 个中期正式条目。
- A3 / A4 已各冻结 `1` 个首发条目，并补齐 `requirement + taskcard_v1`，当前可诚实表述为“主案例已闭环，题库主干已成型，中期题库已补到够用版本”。
- 最小 CLI 原型已建立：`python run_research_case.py --case A2 --mode plain_guidance --track baseline` 可直接输出 prompt、protocol、run 文档和 metrics 摘要。
- 导师演示入口已补出：`python run_research_case.py --demo advisor` 会按“输入题目 -> 结构化表示 -> prompt 选择 -> run 结果 -> metrics 摘要”输出固定演示链条。
- 小样本试用方案已冻结：baseline vs 过程化流程的 `v0` 试用方案、参与者表单、session record、评分表和 CSV 数据结构已预埋。
- 首轮 pilot 的执行顺序已收束：中期后先跑 `T2_A1_bug_01` 和 `T3_A2_bug_01` 的 `4` 人 bug-repair 小样本，不先铺开 implementation 和全部任务。
- 已完成 `1` 次内部 dry run：`2026-04-20` 用 `T2_A1_bug_01 + process_guided_workflow` 完整走通 `participant_form -> session_record -> scoring_sheet -> CSV` 回填链路。
- dry run 后已把 notes template 补上 `session_id` 和最终代码路径，并给 participant form 补了前测 / 后测填写时机提示。
- 首轮 `4` 人 pilot 的排班表、任务包清单，以及 process-guided 条件下要发放的 bug-repair checklist / notes template 已补出。
- 中期汇报 PPT 已整理完成：`report/中期汇报.pptx`。
- 当前中期重点不是继续追加同类 rerun，而是收束模板库、检查清单、错误分类、题库页和原型入口。

## 当前冻结的研究结论
- `plain_guidance` / `coe_guided` 的核心优势，是提升自检覆盖、根因说明和回归说明的可复查性。
- 在 A2 这类冻结协议任务上，结构化 guidance 未必显著改变最终恢复指标，但确实改善了过程质量与可解释性。

## 快速入口
- [task_cards/A1_seam_carving_taskcard_v1.md](task_cards/A1_seam_carving_taskcard_v1.md)
- [task_cards/A1_bug_repair_taskcard_v0.md](task_cards/A1_bug_repair_taskcard_v0.md)
- [task_cards/A2_rslt_inpainting_taskcard_v1.md](task_cards/A2_rslt_inpainting_taskcard_v1.md)
- [task_cards/A2_bug_repair_taskcard_v0.md](task_cards/A2_bug_repair_taskcard_v0.md)
- [problems/a3_requirement.md](problems/a3_requirement.md)
- [task_cards/A3_taskcard_v1.md](task_cards/A3_taskcard_v1.md)
- [problems/a4_requirement.md](problems/a4_requirement.md)
- [task_cards/A4_taskcard_v1.md](task_cards/A4_taskcard_v1.md)
- [report/a1_eval_protocol_v0.md](report/a1_eval_protocol_v0.md)
- [report/a1_replication_summary_v0.md](report/a1_replication_summary_v0.md)
- [report/a1_bug_repair_protocol_v0.md](report/a1_bug_repair_protocol_v0.md)
- [report/a1_bug_repair_summary_v0.md](report/a1_bug_repair_summary_v0.md)
- [report/a1_v1_stage_summary.md](report/a1_v1_stage_summary.md)
- [report/a2_eval_protocol_v0.md](report/a2_eval_protocol_v0.md)
- [report/a2_baseline_summary_v0.md](report/a2_baseline_summary_v0.md)
- [report/a2_replication_summary_v0.md](report/a2_replication_summary_v0.md)
- [report/a2_bug_repair_protocol_v0.md](report/a2_bug_repair_protocol_v0.md)
- [report/a2_failure_case_design_v0.md](report/a2_failure_case_design_v0.md)
- [report/a2_bug_repair_summary_v0.md](report/a2_bug_repair_summary_v0.md)
- [report/a2_expanded_scope_protocol_v0.md](report/a2_expanded_scope_protocol_v0.md)
- [report/a2_expanded_scope_summary_v0.md](report/a2_expanded_scope_summary_v0.md)
- [report/a2_expanded_scope_selected_entries_v1.md](report/a2_expanded_scope_selected_entries_v1.md)
- [report/phase2_progress_report_2026-04-12.md](report/phase2_progress_report_2026-04-12.md)
- [report/中期汇报.pptx](report/中期汇报.pptx)
- [report/timeline_scope_alignment_2026-04-12.md](report/timeline_scope_alignment_2026-04-12.md)
- [report/prompt_template_library_v1.md](report/prompt_template_library_v1.md)
- [report/structured_modeling_checklist_v1.md](report/structured_modeling_checklist_v1.md)
- [report/error_taxonomy_and_feedback_rules_v1.md](report/error_taxonomy_and_feedback_rules_v1.md)
- [report/midterm_stage_summary_v0.md](report/midterm_stage_summary_v0.md)
- [report/midterm_attachment_checklist_v0.md](report/midterm_attachment_checklist_v0.md)
- [report/task_bank_index_v1.md](report/task_bank_index_v1.md)
- [report/task_bank_status_v1.md](report/task_bank_status_v1.md)
- [report/prototype_outline_v0.md](report/prototype_outline_v0.md)
- [report/prototype_cli_v0.md](report/prototype_cli_v0.md)
- [report/advisor_demo_entry_v1.md](report/advisor_demo_entry_v1.md)
- [report/small_sample_pilot_plan_v0.md](report/small_sample_pilot_plan_v0.md)
- [report/pilot_internal_dry_run_v0.md](report/pilot_internal_dry_run_v0.md)
- [report/pilot_internal_dry_run_result_2026-04-20.md](report/pilot_internal_dry_run_result_2026-04-20.md)
- [report/pilot_round1_schedule_v0.md](report/pilot_round1_schedule_v0.md)
- [report/pilot_round1_task_pack_checklist_v0.md](report/pilot_round1_task_pack_checklist_v0.md)
- [report/advisor_confirmation_questions_v0.md](report/advisor_confirmation_questions_v0.md)
- [pilot/pilot_participant_form_v0.md](pilot/pilot_participant_form_v0.md)
- [pilot/pilot_bug_repair_checklist_v0.md](pilot/pilot_bug_repair_checklist_v0.md)
- [pilot/pilot_bug_repair_notes_template_v0.md](pilot/pilot_bug_repair_notes_template_v0.md)
- [pilot/pilot_scoring_sheet_v0.md](pilot/pilot_scoring_sheet_v0.md)
- [pilot/pilot_session_record_template_v0.md](pilot/pilot_session_record_template_v0.md)
- [metrics/a1_guidance_eval_v0.csv](metrics/a1_guidance_eval_v0.csv)
- [metrics/a1_codegen_perf_v0.csv](metrics/a1_codegen_perf_v0.csv)
- [metrics/a1_failure_repair_eval_v0.csv](metrics/a1_failure_repair_eval_v0.csv)
- [metrics/a2_guidance_eval_v0.csv](metrics/a2_guidance_eval_v0.csv)
- [metrics/a2_recovery_perf_v0.csv](metrics/a2_recovery_perf_v0.csv)
- [metrics/a2_failure_repair_eval_v0.csv](metrics/a2_failure_repair_eval_v0.csv)
- [metrics/a2_expanded_scope_eval_v0.csv](metrics/a2_expanded_scope_eval_v0.csv)
- [metrics/a2_expanded_scope_perf_v0.csv](metrics/a2_expanded_scope_perf_v0.csv)
- [metrics/pilot_session_log_template_v0.csv](metrics/pilot_session_log_template_v0.csv)
- [metrics/pilot_session_log_dry_run_v0.csv](metrics/pilot_session_log_dry_run_v0.csv)
- [metrics/pilot_session_log_codebook_v0.md](metrics/pilot_session_log_codebook_v0.md)

## 仓库结构
task_cards / prompts / runs / metrics / report / pilot / solutions / outputs / run_research_case.py

## CLI 原型入口
- 列出支持的 case / mode / track 组合：`python run_research_case.py --list`
- 列出支持的演示模式：`python run_research_case.py --demo list`
- 导师演示模式：`python run_research_case.py --demo advisor`
- 查看 A1 baseline 摘要：`python run_research_case.py --case A1 --mode plain_guidance --track baseline`
- 查看 A2 bug-repair 摘要：`python run_research_case.py --case A2 --mode coe_guided --track bug-repair`
- 查看 A2 expanded-scope 摘要：`python run_research_case.py --case A2 --mode direct_answer --track expanded-scope`
- 说明文档：[report/prototype_cli_v0.md](report/prototype_cli_v0.md)

## A1 复现入口
- 环境基线（统一）：使用 conda 环境 `llmft`，不再把 `.venv` 作为实验主环境。
- 激活命令（PowerShell）：`conda activate llmft`
- 依赖检查：`python -c "import numpy, matplotlib, skimage, scipy; print('deps ok')"`
- 主入口脚本：[solutions/hw1_op1/src/run_step6_comparisons.py](solutions/hw1_op1/src/run_step6_comparisons.py)
- 单条 replication 评测入口示例：`python solutions/hw1_op1/generated/run_015_plain_guidance_rep3/src/run_protocol_eval.py`
- bug-repair 协议：[report/a1_bug_repair_protocol_v0.md](report/a1_bug_repair_protocol_v0.md)
- failure cases 路径：[solutions/hw1_op1/failure_cases](solutions/hw1_op1/failure_cases)
- 输出位置：[outputs/hw1_op1](outputs/hw1_op1)

## 下一步
1. 用 dry run 修过的模板准备首轮 `4` 人 formal pilot 的任务包和记录包。
2. 中期后首轮只跑 `T2_A1_bug_01` 和 `T3_A2_bug_01`，按 `baseline_workflow / process_guided_workflow` 各 `1` 次组成 `4` 人小样本。
3. 首轮 `4` 人试用完成后，先回填正式 session log，再根据首轮反馈决定是否把 `T1_A1_width` 纳入下一轮。
4. 更后续再推进 A3 / A4 首发条目、统一原型封装和更大范围试用。

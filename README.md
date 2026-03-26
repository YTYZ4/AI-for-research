# AI-for-research
一句话目标：用 A1/A2 主案例做“过程化指导 + 结构化检查 + 纠错评估”的研究仓库。

## Current status
- A1 v0 result completed：baseline direct_answer / plain_guidance / coe_guided 已全部跑通。
- A1 failure cases 已整理为可复查资产，可用于后续 bug-repair benchmark。
- A2 仍为 bootstrap-only，尚未进入算法实现。
- 当前阶段：Phase 2（A1 replication + A1 bug-repair benchmark），用于验证趋势稳定性。

## Quick links
- [task_cards/A1_seam_carving_taskcard_v1.md](task_cards/A1_seam_carving_taskcard_v1.md)
- [runs/2026-03-25_run_005_a1_asset_packaging.md](runs/2026-03-25_run_005_a1_asset_packaging.md)
- [report/hw1_op1_report_outline.md](report/hw1_op1_report_outline.md)
- [report/a1_eval_protocol_v0.md](report/a1_eval_protocol_v0.md)
- [report/a1_baseline_vs_coe_v0.md](report/a1_baseline_vs_coe_v0.md)
- [metrics/hw1_op1_metrics.csv](metrics/hw1_op1_metrics.csv)
- [metrics/a1_guidance_eval_v0.csv](metrics/a1_guidance_eval_v0.csv)
- [metrics/a1_codegen_perf_v0.csv](metrics/a1_codegen_perf_v0.csv)
- [metrics/a1_failure_repair_eval_v0.csv](metrics/a1_failure_repair_eval_v0.csv)

## Repo map
task_cards / prompts / runs / metrics / report / solutions / outputs

## Reproduce A1
- 环境：conda create -n mm26 python=3.12；安装 numpy、matplotlib、scikit-image、scipy。
- 入口脚本：[solutions/hw1_op1/src/run_step6_comparisons.py](solutions/hw1_op1/src/run_step6_comparisons.py)
- 数据路径：[solutions/hw1_op1/figs](solutions/hw1_op1/figs)
- 输出位置：[outputs/hw1_op1](outputs/hw1_op1)

## Next milestones
1. A1 replication（同协议复跑 direct/plain/CoE，验证趋势是否稳定）
2. A1 bug-repair benchmark（基于 bug_01/02/03 比较诊断与修复效率）
3. A2 minimal implementation（在 A1 v1 小结后启动代码阶段）

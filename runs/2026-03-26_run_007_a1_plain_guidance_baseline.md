# run 007 - a1 plain guidance baseline

date: 2026-03-26
mode: plain_guidance
prompt_file: prompts/a1/baseline_plain_guidance_v0.md
task_card_version: v1
protocol: report/a1_eval_protocol_v0.md

## objective
测试给定题目要求 + Task Card v1 后，普通指导模式的可运行性与纠错效率。

## generated code path
- solutions/hw1_op1/generated/run_007_plain_guidance/

## execution log
- status: completed
- first_error: none
- fix_steps: none
- runnable: yes
- correct: yes (width shrink + height shrink + compare_grid all generated)

## runtime evidence
- [bing1.png] seam_width 18.324s
- [bing1.png] seam_height 5.225s
- [original.png] seam_width 98.570s
- [original.png] seam_height 80.019s

## artifacts
- prompt: solutions/hw1_op1/generated/run_007_plain_guidance/prompt_used.md
- raw response: solutions/hw1_op1/generated/run_007_plain_guidance/model_raw_response.md
- code: solutions/hw1_op1/generated/run_007_plain_guidance/src/
- outputs: outputs/hw1_op1/run_007_plain_guidance/

## stability observations
- 相比 run 006，本轮没有出现首轮路径级错误。
- 输出中给出了 Task Card 对齐的检查项，并落实为代码断言。
- 未出现“只说检查不做检查”的情况（代码里有 seam 连续性/边界/维度/能量重算断言）。

## required outputs
- seam_width / seam_height / compare_grid (按固定协议)

## notes
- 首次可运行无修复轮次，但在 original.png 上运行时间明显偏高。

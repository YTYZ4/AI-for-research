# run 008 - a1 coe guided

date: 2026-03-27
mode: coe_guided
prompt_file: prompts/a1/coe_multi_role_v0.md
task_card_version: v1
protocol: report/a1_eval_protocol_v0.md

## objective
测试多角色结构化指导（CoE）在 A1 任务上的稳定性、纠错轮次和首个可运行时间。

## generated code path
- solutions/hw1_op1/generated/run_008_coe_guided/

## execution log
- status: completed
- first_error: none
- fix_steps: none
- runnable: yes
- correct: yes (width shrink + height shrink + compare_grid all generated)

## runtime evidence
- [bing1.png] seam_width 90.496s
- [bing1.png] seam_height 16.699s
- [original.png] seam_width 118.965s
- [original.png] seam_height 17.699s

## artifacts
- prompt: solutions/hw1_op1/generated/run_008_coe_guided/prompt_used.md
- raw response: solutions/hw1_op1/generated/run_008_coe_guided/model_raw_response.md
- code: solutions/hw1_op1/generated/run_008_coe_guided/src/
- outputs: outputs/hw1_op1/run_008_coe_guided/

## four focus checks for CoE
- Reader 有没有把验收条件说清楚：yes（明确 shrink-only + width/height + compare_grid）
- Planner 有没有把函数拆分写完整：yes（完整覆盖 5 个最小函数 + 主接口）
- Coder 有没有写出自检断言：yes（seam 连续性、边界、维度、能量重算）
- Reviewer 有没有按 5 类错误逐项检查：yes（raw response 中逐项点名并给修复建议）

## required outputs
- seam_width / seam_height / compare_grid (按固定协议)

## notes
- CoE 版本在结构化检查性方面最完整，但本次运行耗时最高。

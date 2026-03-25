# run 006 - a1 direct answer baseline

date: 2026-03-26
mode: direct_answer
prompt_file: prompts/a1/baseline_direct_answer_v0.md
task_card_version: none
protocol: report/a1_eval_protocol_v0.md

## objective
测试在不提供 Task Card 和错误清单情况下，模型是否能稳定完成 A1 shrink 版本。

## generated code path
- solutions/hw1_op1/generated/run_006_direct_answer/

## execution log
- status: completed
- first_error: FileNotFoundError (repo root path resolved incorrectly; looked for solutions/solutions/hw1_op1/figs)
- fix_steps: updated generated evaluator path root from parents[4] to parents[5], then reran protocol
- runnable: yes
- correct: yes (width shrink + height shrink + compare_grid all generated)

## runtime evidence
- [bing1.png] seam_width 18.420s
- [bing1.png] seam_height 5.219s
- [original.png] seam_width 34.745s
- [original.png] seam_height 17.796s

## artifacts
- prompt: solutions/hw1_op1/generated/run_006_direct_answer/prompt_used.md
- raw response: solutions/hw1_op1/generated/run_006_direct_answer/model_raw_response.md
- code: solutions/hw1_op1/generated/run_006_direct_answer/src/
- outputs: outputs/hw1_op1/run_006_direct_answer/

## required outputs
- seam_width / seam_height / compare_grid (按固定协议)

## notes
- 本次首次失败属于 other（路径配置错误），非 seam 算法核心错误。
- 自检信息仅弱描述，缺少明确断言。

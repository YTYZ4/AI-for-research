# a1 failure repair codebook v0

适用范围：
- metrics/a1_failure_repair_eval_v0.csv

目标：
- 固定 A1 failure case 修复实验的打分口径

字段定义：

run_id：
- 格式：YYYY-MM-DD_run_xxx

bug_id：固定允许值
- bug_01_dp_boundary
- bug_02_no_energy_recompute
- bug_03_height_transpose

mode：只允许
- direct_answer
- plain_guidance
- coe_guided

diagnosis_correct：0/1
- 0 = 没定位到主错误
- 1 = 主错误定位正确

patch_runnable：0/1
- 0 = 修补后不能跑
- 1 = 修补后能跑

regression_pass：0/1
- 0 = 修补后回归测试未通过
- 1 = 修补后回归测试通过

fix_rounds：非负整数

time_to_fix_min：分钟；未修好填 NA

notes：写触发条件、关键修补点、残留问题

填表规则：
- 一次 bug-repair run 只保留一行主记录
- 必须先写 symptom / diagnosis / patch 事实，再回填 CSV

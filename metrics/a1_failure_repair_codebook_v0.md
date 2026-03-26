# a1 failure repair codebook v0

适用范围：
- metrics/a1_failure_repair_eval_v0.csv
- solutions/hw1_op1/failure_cases/ 下 bug-repair 对照实验

目标：
- 固定三类错误样例与修复评价口径。
- 比较不同 guidance mode 的诊断准确性与修复效率。

## 字段定义与取值

### run_id
- 格式：YYYY-MM-DD_run_xxx
- 示例：2026-03-26_run_016

### bug_id
- 固定允许值：
  - bug_01_dp_boundary
  - bug_02_no_energy_recompute
  - bug_03_height_transpose

### mode
- 允许值：direct_answer / plain_guidance / coe_guided

### diagnosis_correct
- 0 = 未正确定位根因
- 1 = 正确定位根因

### patch_runnable
- 0 = 修复代码不可运行
- 1 = 修复代码可运行

### regression_pass
- 0 = 回归测试未通过
- 1 = 回归测试通过

### fix_rounds
- 非负整数。
- 从首次失败到回归通过之间的修复轮次。
- 若未通过，记录已发生轮次并在 notes 说明中止原因。

### time_to_fix_min
- 单位：分钟。
- 从开始修复到首次回归通过的耗时。
- 若未通过，填 NA。

### notes
- 简短记录：
  - 触发条件
  - 核心补丁点
  - 未通过原因（如有）

## 填表规则
- 每个 run_id + bug_id 保留一行。
- 三种 mode 建议对同一 bug 使用相同测试输入与回归脚本。
- 若测试协议变更，必须在 notes 明确标注。

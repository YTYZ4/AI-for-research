# a1 guidance eval codebook v0

适用范围：
- metrics/a1_guidance_eval_v0.csv
- run 006 / run 007 / run 008 及后续 A1 guidance 对照实验

目标：
- 固定字段取值，避免不同 run 使用不一致口径。

## 字段定义与取值

### run_id
- 格式：YYYY-MM-DD_run_xxx
- 示例：2026-03-26_run_006

### case_id
- 当前固定为：A1

### mode
- 允许值：direct_answer / plain_guidance / coe_guided

### prompt_file
- 对应提示文件路径。
- 例如：prompts/a1/baseline_direct_answer_v0.md

### task_card_version
- 允许值：none / v1
- direct_answer 通常为 none，plain_guidance 与 coe_guided 通常为 v1。

### artifact_complete
- 0 = 核心产物不全
- 1 = 有代码，但输出图或 run 记录缺项
- 2 = 代码、协议输出图、run 记录都齐

### runnable
- 0 = 不能跑
- 1 = 能跑

### correct
- 0 = 不满足 A1
- 1 = 部分满足（只宽或只高）
- 2 = 宽 / 高 / compare_grid 都满足

### self_check
- 0 = 无
- 1 = 口头提到检查（例如“应检查 seam 连续性/维度”）
- 2 = 有明确断言或验证步骤（例如 seam 相邻行差值、删除后维度、转置前后 shape、dtype/像素范围）

### error_type
- 允许值：
  - dp_boundary
  - seam_discontinuous
  - no_energy_recompute
  - height_transpose
  - dtype_range
  - other
  - none

### fix_rounds
- 非负整数。
- 首轮就能跑通 = 0；首轮失败改一次后跑通 = 1；依此类推。

### time_to_first_working_min
- 单位：分钟。
- 建议使用一位或两位小数。
- 若未跑通，填 NA。

### notes
- 简短备注：
  - 触发条件
  - 关键修复动作
  - 与协议偏差（如有）

## 填表规则
- 先在 runs 文档记录事实，再回填 CSV。
- 同一 run 只保留一行主记录；若需要细分，可在 notes 中补充。
- 若偏离 report/a1_eval_protocol_v0.md，必须在 notes 明确写出偏离原因。

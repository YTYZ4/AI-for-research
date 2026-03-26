# a1 codegen perf codebook v0

适用范围：
- metrics/a1_codegen_perf_v0.csv
- A1 replication runs（run_010 及之后）

目标：
- 将“指导效率”和“生成代码运行性能”分离记录。
- 固定字段口径，避免 method 含义混用。

## 字段定义与取值

### run_id
- 格式：YYYY-MM-DD_run_xxx
- 示例：2026-03-26_run_010

### image_name
- 允许值：bing1.png / original.png

### method
- 固定含义：guidance mode（不是图像算法方法名）。
- 允许值：direct_answer / plain_guidance / coe_guided

### width_runtime_s
- 单位：秒。
- 记录 seam_width 的运行时间。

### height_runtime_s
- 单位：秒。
- 记录 seam_height 的运行时间。

### total_runtime_s
- 单位：秒。
- 计算方式：width_runtime_s + height_runtime_s。
- 建议保留三位小数。

### output_ok
- 0 = 输出不完整或不可用
- 1 = 输出完整且可用

### notes
- 简短记录异常情况：
  - 超时
  - 中断重跑
  - 参数偏离协议（若有）

## 填表规则
- 每个 run_id 对每张图各一行（通常每个 run 2 行）。
- 若偏离 report/a1_eval_protocol_v0.md，必须在 notes 写明偏离原因和影响。
- 本表仅描述运行性能，不用于评价 runnable/correct/self_check。

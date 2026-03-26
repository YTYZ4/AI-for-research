# a1 codegen perf codebook v0

适用范围：
- metrics/a1_codegen_perf_v0.csv

目标：
- 分离“guidance 质量”和“生成代码运行性能”。

字段定义：

run_id：
- 格式：YYYY-MM-DD_run_xxx

image_name：
- 固定为 bing1.png / original.png

method：这里固定解释为 guidance mode，只允许
- direct_answer
- plain_guidance
- coe_guided

width_runtime_s：该图上完成 width shrink 全流程耗时（秒）

height_runtime_s：该图上完成 height shrink 全流程耗时（秒）

total_runtime_s：同一图上的总耗时；口径固定为 width + height + compare 输出

output_ok：0/1
- 0 = 该图协议输出不完整、不可检查，或结果明显异常
- 1 = 该图 width/height/compare 输出都完整，且结果不是明显坏图

notes：记录异常、协议偏离、特殊说明

填表规则：
- 每个 run 每张图一行，因此一个 run 默认写 2 行
- 不把 seam_width / crop / resize_linear 填到 method
- 若偏离 report/a1_eval_protocol_v0.md，必须在 notes 写明

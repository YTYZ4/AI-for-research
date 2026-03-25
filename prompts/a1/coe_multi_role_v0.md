# coe multi role v0

模式：coe_guided
目的：在 A1 任务上使用固定多角色结构输出，提升可复现性与纠错稳定性。

输入材料（必须提供）：
1. 题目要求（hw_1/op_1）
2. task_cards/A1_seam_carving_taskcard_v1.md
3. report/a1_eval_protocol_v0.md
4. 当前实现代码与运行日志（如果有）

统一约束：
1. 只做 shrink，不做 enlarge。
2. 主接口为 seam_carve_image(im, sz)。
3. 最小函数拆分遵循 Task Card：compute_energy / find_vertical_seam / remove_vertical_seam / seam_carve_width / seam_carve_height。
4. 后续所有 A1 CoE run 必须使用以下固定标题，不允许缺失角色。

## Role 1 Reader
- 题目重述
- 输入/输出
- 验收条件

## Role 2 Planner
- 算法步骤
- 函数拆分
- 边界与风险点

## Role 3 Coder
- 代码骨架
- 关键实现
- 需要自检的断言

## Role 4 Reviewer
- 对照 Task Card 的 5 类常见错误逐项检查
- 列出最可能失败点
- 给修复建议

Reviewer 检查表（直接对照 Task Card，不另起炉灶）：
1. DP 边界越界
2. seam 不连续
3. 删除 seam 后维度不对
4. 高度转置复用出错
5. dtype/像素范围异常

## Role 5 Experimenter
- 固定测试图
- 固定目标尺寸
- 对比方法
- 记录项与结果总结

评估落地：
1. 严格按 report/a1_eval_protocol_v0.md 运行。
2. 结果记录到 runs/2026-03-27_run_008_a1_coe_guided.md。
3. 指标写入 metrics/a1_guidance_eval_v0.csv。

# prompt used - run 008 coe_guided

请严格使用 prompts/a1/coe_multi_role_v0.md 的固定五角色结构输出并完成 A1。

必须包含：
- Role 1 Reader: 题目重述 / 输入输出 / 验收条件
- Role 2 Planner: 算法步骤 / 函数拆分 / 边界风险
- Role 3 Coder: 代码骨架 / 关键实现 / 自检断言
- Role 4 Reviewer: 对 Task Card 五类错误逐项检查 + 失败点 + 修复建议
- Role 5 Experimenter: 固定测试图 / 固定目标尺寸 / 对比方法 / 记录项总结

实验约束：
- 严格按 report/a1_eval_protocol_v0.md
- shrink-only
- 输出到 outputs/hw1_op1/run_008_coe_guided/

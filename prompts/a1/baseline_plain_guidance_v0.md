# baseline plain_guidance v0

模式：plain_guidance
目的：给题目要求 + Task Card v1，但不使用多角色分工，观察普通结构化指导的效果。

输入给模型的信息：
1. 作业要求（hw_1/op_1）
2. Task Card：task_cards/A1_seam_carving_taskcard_v1.md
3. 约束：先保正确与可运行，保持 shrink-only 口径
4. 交付：代码、对比图、run 记录、metrics 条目

评估执行：
- 按 report/a1_eval_protocol_v0.md 固定协议跑。
- 结果填入 metrics/a1_guidance_eval_v0.csv。

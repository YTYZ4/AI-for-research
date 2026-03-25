# baseline direct_answer v0

模式：direct_answer
目的：只给题目要求，不给 Task Card，不给错误清单，观察模型直接产出代码时的稳定性。

输入给模型的最小信息：
1. 课程作业：hw_1/op_1（Seam Carving）
2. 目标函数：seam_carve_image(im, sz)
3. 输出要求：可运行代码 + 宽度/高度缩小结果 + 与 resize/crop 对比
4. 限制：当前阶段只要求 shrink，不做 enlarge

评估执行：
- 按 report/a1_eval_protocol_v0.md 固定协议跑。
- 结果填入 metrics/a1_guidance_eval_v0.csv。

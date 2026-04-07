# prompt used - run 013 plain_guidance rep1

你是一个代码助手。请基于作业要求和 Task Card，完成 A1 shrink-only Seam Carving 的可运行实现与协议化评测脚本。

材料 1：problems/hw1_op1_requirement.md
- 任务：实现内容感知缩放，主接口 seam_carve_image(im, sz)
- 输出：代码 + 宽度/高度缩小结果 + 与 crop/resize 对比
- 本轮限制：只做 shrink，不做 enlarge

材料 2：prompts/a1/baseline_plain_guidance_v0.md
- plain_guidance 模式：给题目要求 + Task Card v1，但不使用多角色分工
- 评测按 report/a1_eval_protocol_v0.md 固定协议执行

材料 3：task_cards/A1_seam_carving_taskcard_v1.md
- 最小函数拆分：compute_energy / find_vertical_seam / remove_vertical_seam / seam_carve_width / seam_carve_height / seam_carve_image
- 常见错误自检：DP 边界、seam 连续性、删除后维度、高度转置、dtype/range

交付要求：
1. 生成可运行实现代码（shrink-only）
2. 生成协议执行脚本，固定：
- 测试图：bing1.png、original.png
- 预处理：max_side=420
- 任务：width shrink + height shrink
- 输出：original / resize_linear / crop / seam_width / seam_height / compare_grid
3. 路径固定：
- 代码：solutions/hw1_op1/generated/run_013_plain_guidance_rep1/src/
- 输出：outputs/hw1_op1/run_013_plain_guidance_rep1/
4. 不使用 CoE 五角色标题。

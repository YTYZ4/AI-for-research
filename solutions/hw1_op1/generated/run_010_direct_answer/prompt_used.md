# prompt used - run 010 direct_answer

你是一个代码助手。请直接完成 hw_1/op_1 的 Python 版本 Seam Carving。

主提示来源：prompts/a1/baseline_direct_answer_v0.md
附加题目要求来源：problems/hw1_op1_requirement.md

已知信息（仅这些）：
1. 课程作业：hw_1/op_1（Seam Carving）
2. 目标函数：seam_carve_image(im, sz)
3. 输出要求：可运行代码 + 宽度/高度缩小结果 + 与 resize/crop 对比
4. 限制：当前阶段只要求 shrink，不做 enlarge

请给出：
1. 一份可运行的 seam carving 实现（包含最小函数拆分）
2. 一份实验脚本：
- 固定测试图 bing1.png 和 original.png
- 固定预处理 max_side=420
- 固定任务 width shrink 和 height shrink
- 输出每个 case 的 original.png / resize_linear.png / crop.png / seam_width.png / seam_height.png / compare_grid.png
3. 输出目录使用：outputs/hw1_op1/run_010_direct_answer/
4. 给出代码后不要省略关键实现。

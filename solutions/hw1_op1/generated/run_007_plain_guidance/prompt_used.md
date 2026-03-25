# prompt used - run 007 plain_guidance

请完成 A1 Seam Carving（hw_1/op_1）shrink-only 版本。

输入信息：
1. 作业要求：实现 seam_carve_image(im, sz)，并给出 width/height shrink 与 resize/crop 对比。
2. Task Card：task_cards/A1_seam_carving_taskcard_v1.md
3. 固定协议：report/a1_eval_protocol_v0.md

要求：
1. 给出可运行代码，建议函数拆分：compute_energy / find_vertical_seam / remove_vertical_seam / seam_carve_width / seam_carve_height。
2. 明确自检断言（seam 连续性、维度变化、能量重算）。
3. 提供评测脚本，输出到 outputs/hw1_op1/run_007_plain_guidance/。
4. 当前仅做 shrink，不做 enlarge。

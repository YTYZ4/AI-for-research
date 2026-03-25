# model raw response - run 008 coe_guided

## Role 1 Reader
- 题目重述
  - 任务是实现 A1 Seam Carving 的 shrink-only 版本，主接口为 seam_carve_image(im, sz)。
- 输入/输出
  - 输入：RGB 图像 im，目标尺寸 sz=(target_h, target_w)
  - 输出：缩小后的图像，以及协议要求的对比图产物
- 验收条件
  - 能完成 width shrink 和 height shrink
  - 输出 compare_grid
  - 通过固定测试图与固定预处理协议

## Role 2 Planner
- 算法步骤
  1. 计算能量图
  2. DP 累计最小代价
  3. 回溯 seam
  4. 删除 seam
  5. 迭代缩宽
  6. 转置复用缩高
- 函数拆分
  - compute_energy
  - find_vertical_seam
  - remove_vertical_seam
  - seam_carve_width
  - seam_carve_height
  - seam_carve_image
- 边界与风险点
  - DP 边界越界
  - seam 不连续
  - 删除后维度不对
  - 高度转置轴错误
  - dtype/范围异常

## Role 3 Coder
- 代码骨架
  - seam_carving_generated.py + run_protocol_eval.py
- 关键实现
  - shrink-only，先宽后高
  - 固定协议输出目录 outputs/hw1_op1/run_008_coe_guided
- 需要自检的断言
  - seam continuity, seam bounds, energy-shape consistency, width decrement

## Role 4 Reviewer
- 对照 Task Card 的 5 类常见错误逐项检查
  1. DP 边界越界：已通过 left/right clamp 规避
  2. seam 不连续：有 abs(diff)<=1 断言
  3. 删除后维度不对：有 width-1 断言
  4. 高度转置复用出错：使用 (1,0,2) 转置与逆转置
  5. dtype/像素范围异常：统一 to_uint8
- 列出最可能失败点
  - 数据路径拼接错误
  - 大图耗时过长导致误判超时
- 给修复建议
  - 固定 repo_root 解析
  - 使用 max_side=420 限幅

## Role 5 Experimenter
- 固定测试图
  - bing1.png, original.png
- 固定目标尺寸
  - width=0.8*w, height=0.85*h（预处理后）
- 对比方法
  - resize_linear, crop, seam_width, seam_height
- 记录项与结果总结
  - 记录 runnable/correct/fix_rounds/time/error_type/self_check 到 guidance eval 表

代码文件已提供于 src/ 目录。

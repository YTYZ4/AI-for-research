# A1 evaluation protocol v0

固定测试图：
1. bing1.png
2. original.png

固定预处理：
- max_side = 420

固定目标任务：
1. width shrink
2. height shrink

固定作业级对照：
1. resize_linear
2. crop
3. seam_width
4. seam_height

固定研究级对照：
1. direct_answer
2. plain_guidance
3. coe_guided

执行约束：
- 后续 A1 run 默认沿用本协议，不随意更换测试图、预处理参数和任务口径。
- 若有偏离，必须在对应 run 文档与 metrics 中显式标注原因与影响。

# symptom
现象：
- 在处理边界列时可能抛出 IndexError。
- 即使未崩溃，也可能因负索引误用导致 seam 路径异常跳变。

触发条件：
- 测试图：bing1.png 或 original.png
- 目标尺寸：例如 target=(128,336) 的 width shrink 过程

归类：
- 代码错误

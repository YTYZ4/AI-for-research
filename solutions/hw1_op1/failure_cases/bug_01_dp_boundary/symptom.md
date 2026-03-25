# symptom
现象：
- 报什么错 / 输出什么异常结果
- 在处理边界列时可能抛出 IndexError，或由于负索引误用导致 seam 异常跳变。

触发条件：
- 哪张图
- bing1.png 或 original.png
- 哪个 target size
- 例如 target=(128,336) 的 width shrink 过程

归类：
- 建模错误 / 代码错误 / 求解异常 / 结果解释不足
- 代码错误

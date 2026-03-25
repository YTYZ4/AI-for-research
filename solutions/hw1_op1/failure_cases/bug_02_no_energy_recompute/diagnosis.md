# diagnosis

问题原因：
- seam 删除后图像形状变化，但能量图仍使用旧尺寸和旧像素。
- 后续 seam 是在过期能量图上求得，导致索引与当前图像不一致。

定位方法：
1. 在每轮循环打印 out.shape 与 energy.shape。
2. 发现第二轮开始二者不一致即确认问题。

修复要点：
- 每删除一条 seam 后必须重算能量图。
- 可在循环中加入 assert energy.shape == out.shape[:2]。

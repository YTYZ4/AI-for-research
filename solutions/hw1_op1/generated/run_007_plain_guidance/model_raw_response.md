# model raw response - run 007 plain_guidance

基于题目要求 + Task Card v1，给出 shrink-only 实现与协议化实验脚本。

实现说明（plain guidance）：
- 函数拆分：compute_energy / find_vertical_seam / remove_vertical_seam / seam_carve_width / seam_carve_height / seam_carve_image
- 自检断言：
  1. seam 连续性：abs(diff(seam)) <= 1
  2. seam 边界：0 <= seam < w
  3. 删除后维度：new_w = old_w - 1
  4. 每轮重算能量：assert energy.shape == image.shape[:2]

```python
# see src/seam_carving_generated.py
```

```python
# see src/run_protocol_eval.py
```

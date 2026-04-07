# model raw response - run 013 plain_guidance rep1

基于作业要求 + Task Card v1，下面给出 shrink-only Seam Carving 实现与固定协议评测脚本。

实现要点：
- 函数拆分：compute_energy / find_vertical_seam / remove_vertical_seam / seam_carve_width / seam_carve_height / seam_carve_image
- 自检断言（明确验证步骤）：
  1. seam 连续性：abs(diff(seam)) <= 1
  2. seam 边界：0 <= seam < w
  3. 删除后维度：new_w = old_w - 1
  4. 每轮重算能量：energy.shape == image.shape[:2]
  5. shrink-only 限制：target 不得大于原图

```python
# see src/seam_carving_generated.py
```

```python
# see src/run_protocol_eval.py
```

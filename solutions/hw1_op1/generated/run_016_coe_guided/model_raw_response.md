# model raw response - run 016 coe_guided

## Role 1 Reader
- 题目重述
  - 任务是实现 A1 Seam Carving 的 shrink-only 版本，主接口 seam_carve_image(im, sz)。
- 输入/输出
  - 输入：RGB 图像 im，目标尺寸 sz=(target_h, target_w)
  - 输出：缩小后图像，以及协议要求的对比图产物
- 验收条件
  - 完成 width shrink 和 height shrink
  - 生成 compare_grid
  - 按固定协议跑 bing1.png 和 original.png，max_side=420

## Role 2 Planner
- 算法步骤
  1. 计算能量图
  2. DP 累积最小代价
  3. 回溯 seam
  4. 删除 seam
  5. 循环完成 width shrink
  6. 转置复用完成 height shrink
- 函数拆分
  - compute_energy
  - find_vertical_seam
  - remove_vertical_seam
  - seam_carve_width
  - seam_carve_height
  - seam_carve_image
- 边界与风险点
  - DP 边界
  - seam 连续性
  - 删除后维度
  - height 转置
  - dtype/range

## Role 3 Coder
- 代码骨架
  - seam_carving_generated.py + run_protocol_eval.py
- 关键实现
  - shrink-only，先宽后高
- 自检断言
  - seam 连续性
  - seam 索引范围
  - 删除后维度正确
  - 能量图维度一致

```python
# seam_carving_generated.py
from scipy import ndimage
import numpy as np

LAPLACIAN_KERNEL = np.array([[0.5, 1.0, 0.5], [1.0, -6.0, 1.0], [0.5, 1.0, 0.5]], dtype=np.float64)


def compute_energy(im):
    im_f = im.astype(np.float64)
    e = np.zeros(im_f.shape[:2], dtype=np.float64)
    for c in range(im_f.shape[2]):
        lap = ndimage.convolve(im_f[:, :, c], LAPLACIAN_KERNEL, mode='reflect')
        e += lap ** 2
    return e


def find_vertical_seam(energy):
    h, w = energy.shape
    dp = np.zeros((h, w), dtype=np.float64)
    parent = np.zeros((h, w), dtype=np.int32)
    dp[0] = energy[0]

    for i in range(1, h):
        for j in range(w):
            left = max(j - 1, 0)
            right = min(j + 1, w - 1)
            prev = dp[i - 1, left:right + 1]
            k = int(np.argmin(prev))
            best_prev = left + k
            parent[i, j] = best_prev
            dp[i, j] = energy[i, j] + dp[i - 1, best_prev]

    seam = np.zeros(h, dtype=np.int32)
    seam[h - 1] = int(np.argmin(dp[h - 1]))
    for i in range(h - 2, -1, -1):
        seam[i] = parent[i + 1, seam[i + 1]]

    if h > 1:
        assert np.all(np.abs(np.diff(seam)) <= 1)
    assert np.all((seam >= 0) & (seam < w))
    return seam


def remove_vertical_seam(im, seam):
    h, w = im.shape[:2]
    mask = np.ones((h, w), dtype=bool)
    mask[np.arange(h), seam] = False
    out = im[mask].reshape(h, w - 1, im.shape[2])
    assert out.shape[1] == w - 1
    return out


def seam_carve_width(im, target_w):
    out = im.copy()
    target_w = int(target_w)
    while out.shape[1] > target_w:
        energy = compute_energy(out)
        assert energy.shape == out.shape[:2]
        seam = find_vertical_seam(energy)
        out = remove_vertical_seam(out, seam)
    return out


def seam_carve_height(im, target_h):
    t = np.transpose(im, (1, 0, 2))
    t_out = seam_carve_width(t, target_h)
    out = np.transpose(t_out, (1, 0, 2))
    return out


def seam_carve_image(im, sz):
    target_h, target_w = int(sz[0]), int(sz[1])
    h, w = im.shape[:2]
    if target_h > h or target_w > w:
        raise ValueError('shrink-only baseline')

    out = seam_carve_width(im, target_w)
    out = seam_carve_height(out, target_h)
    return out
```

```python
# run_protocol_eval.py
from pathlib import Path
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
from skimage import io
from skimage.transform import resize

from seam_carving_generated import seam_carve_image


def to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img, 0, 255).astype(np.uint8)


def resize_linear(im, target_h, target_w):
    out = resize(im, (target_h, target_w, im.shape[2]), order=1, preserve_range=True, anti_aliasing=True)
    return to_uint8(out)


def center_crop(im, target_h, target_w):
    h, w = im.shape[:2]
    top = max(0, (h - target_h) // 2)
    left = max(0, (w - target_w) // 2)
    return im[top:top + target_h, left:left + target_w].copy()


def downscale_for_runtime(im, max_side=420):
    h, w = im.shape[:2]
    longest = max(h, w)
    if longest <= max_side:
        return im
    scale = max_side / float(longest)
    nh = max(1, int(h * scale))
    nw = max(1, int(w * scale))
    return resize_linear(im, nh, nw)


def save_grid(path, items):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, (name, img) in zip(axes.flat, items):
        ax.imshow(img)
        ax.set_title(name)
        ax.axis('off')
    for ax in axes.flat[len(items):]:
        ax.axis('off')
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    root = Path(__file__).resolve().parents[5]
    figs = root / 'solutions' / 'hw1_op1' / 'figs'
    out_root = root / 'outputs' / 'hw1_op1' / 'run_016_coe_guided'
    out_root.mkdir(parents=True, exist_ok=True)

    rows = []
    cases = [('bing1.png', 'case_subject_bing1'), ('original.png', 'case_landscape_original')]
    for image_name, case_name in cases:
        case_ok = 1
        im = io.imread(str(figs / image_name))
        if im.ndim == 3 and im.shape[2] == 4:
            im = im[:, :, :3]
        im = to_uint8(im)
        im = downscale_for_runtime(im, max_side=420)

        h, w = im.shape[:2]
        target_w = max(1, int(w * 0.8))
        target_h = max(1, int(h * 0.85))

        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        io.imsave(str(case_dir / 'original.png'), im)
        resize_img = resize_linear(im, target_h, target_w)
        io.imsave(str(case_dir / 'resize_linear.png'), resize_img)
        crop_img = center_crop(im, target_h, target_w)
        io.imsave(str(case_dir / 'crop.png'), crop_img)

        t0 = time.perf_counter()
        seam_width = seam_carve_image(im, (h, target_w))
        width_runtime = time.perf_counter() - t0
        print(f'[{image_name}] seam_width {width_runtime:.3f}s')
        io.imsave(str(case_dir / 'seam_width.png'), seam_width)

        t0 = time.perf_counter()
        seam_height = seam_carve_image(im, (target_h, w))
        height_runtime = time.perf_counter() - t0
        print(f'[{image_name}] seam_height {height_runtime:.3f}s')
        io.imsave(str(case_dir / 'seam_height.png'), seam_height)

        t0 = time.perf_counter()
        save_grid(str(case_dir / 'compare_grid.png'), [
            ('original', im),
            ('resize_linear', resize_img),
            ('crop', crop_img),
            ('seam_width', seam_width),
            ('seam_height', seam_height),
        ])
        compare_runtime = time.perf_counter() - t0
        total_runtime = width_runtime + height_runtime + compare_runtime

        rows.append([
            image_name,
            f'{width_runtime:.4f}',
            f'{height_runtime:.4f}',
            f'{total_runtime:.4f}',
            case_ok,
        ])

    with (out_root / 'runtime_metrics.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['image_name', 'width_runtime_s', 'height_runtime_s', 'total_runtime_s', 'output_ok'])
        w.writerows(rows)


if __name__ == '__main__':
    main()
```

## Role 4 Reviewer
- 对照 Task Card 的 5 类常见错误逐项检查
  1. DP 边界越界：使用 left/right clamp，已覆盖
  2. seam 不连续：有 abs(diff)<=1 断言
  3. 删除后维度不对：有宽度递减断言
  4. 高度转置复用出错：使用 (1,0,2) 转置与逆转置
  5. dtype/像素范围异常：统一 to_uint8
- 最可能失败点
  - 路径拼接错误
  - 大图耗时导致误判
- 修复建议
  - 固定 repo_root
  - 固定 max_side=420

## Role 5 Experimenter
- 固定测试图：bing1.png / original.png
- 固定目标：width shrink + height shrink
- 对比输出：original / resize_linear / crop / seam_width / seam_height / compare_grid
- 记录项：runnable/correct/fix_rounds/time/self_check 和每图 runtime

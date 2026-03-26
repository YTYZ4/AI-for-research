# model raw response - run 010 direct_answer

下面给出一个可运行的 shrink-only Seam Carving 实现和协议执行脚本。

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
            parent[i, j] = left + k
            dp[i, j] = energy[i, j] + prev[k]

    seam = np.zeros(h, dtype=np.int32)
    seam[h - 1] = int(np.argmin(dp[h - 1]))
    for i in range(h - 2, -1, -1):
        seam[i] = parent[i + 1, seam[i + 1]]
    return seam


def remove_vertical_seam(im, seam):
    h, w = im.shape[:2]
    mask = np.ones((h, w), dtype=bool)
    mask[np.arange(h), seam] = False
    return im[mask].reshape(h, w - 1, im.shape[2])


def seam_carve_width(im, target_w):
    out = im.copy()
    while out.shape[1] > target_w:
        energy = compute_energy(out)
        seam = find_vertical_seam(energy)
        out = remove_vertical_seam(out, seam)
    return out


def seam_carve_height(im, target_h):
    t = np.transpose(im, (1, 0, 2))
    t_out = seam_carve_width(t, target_h)
    return np.transpose(t_out, (1, 0, 2))


def seam_carve_image(im, sz):
    target_h, target_w = int(sz[0]), int(sz[1])
    if target_h > im.shape[0] or target_w > im.shape[1]:
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
    out_root = root / 'outputs' / 'hw1_op1' / 'run_010_direct_answer'
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

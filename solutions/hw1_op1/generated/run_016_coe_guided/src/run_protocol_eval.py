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

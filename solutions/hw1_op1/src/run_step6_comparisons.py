from pathlib import Path
import csv
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from skimage.transform import resize


def to_uint8(img):
    if img.dtype == np.uint8:
        return img
    return np.clip(img, 0, 255).astype(np.uint8)


def center_crop(im, target_h, target_w):
    h, w = im.shape[:2]
    top = max(0, (h - target_h) // 2)
    left = max(0, (w - target_w) // 2)
    return im[top:top + target_h, left:left + target_w].copy()


def resize_linear(im, target_h, target_w):
    out = resize(
        im,
        (target_h, target_w, im.shape[2]) if im.ndim == 3 else (target_h, target_w),
        order=1,
        preserve_range=True,
        anti_aliasing=True,
    )
    return to_uint8(out)


def downscale_for_runtime(im, max_side=420):
    """Downscale very large images so the pure-Python seam loop can finish quickly."""
    h, w = im.shape[:2]
    longest = max(h, w)
    if longest <= max_side:
        return im
    scale = max_side / float(longest)
    new_h = max(1, int(h * scale))
    new_w = max(1, int(w * scale))
    return resize_linear(im, new_h, new_w)


def save_compare_grid(out_path, images_with_title):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, (title, img) in zip(axes.flat, images_with_title):
        ax.imshow(img)
        ax.set_title(title)
        ax.axis('off')

    # Fill any unused cells with empty view.
    for ax in axes.flat[len(images_with_title):]:
        ax.axis('off')

    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main():
    repo_root = Path(__file__).resolve().parents[3]
    ref_dir = repo_root / 'solutions' / 'hw1_op1' / 'reference_template'
    sys.path.insert(0, str(ref_dir))

    from seam_carving import seam_carve_image

    figs_dir = repo_root / 'solutions' / 'hw1_op1' / 'figs'
    output_root = repo_root / 'outputs' / 'hw1_op1'
    output_root.mkdir(parents=True, exist_ok=True)

    cases = [
        ('bing1.png', 'case_subject_bing1'),
        ('original.png', 'case_landscape_original'),
    ]

    metrics_rows = []
    run_id = '2026-03-25_run_004'

    for image_name, case_name in cases:
        src_path = figs_dir / image_name
        case_dir = output_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        im = io.imread(str(src_path))
        if im.ndim == 3 and im.shape[2] == 4:
            im = im[:, :, :3]
        im = to_uint8(im)
        im = downscale_for_runtime(im, max_side=420)

        h, w = im.shape[:2]
        target_w = max(1, int(w * 0.8))
        target_h = max(1, int(h * 0.85))

        print(f'[case] {image_name}: input={h}x{w}, target={target_h}x{target_w}')

        io.imsave(str(case_dir / 'original.png'), im)

        # resize linear
        t0 = time.perf_counter()
        resize_img = resize_linear(im, target_h, target_w)
        t_resize = time.perf_counter() - t0
        io.imsave(str(case_dir / 'resize_linear.png'), resize_img)
        metrics_rows.append([run_id, image_name, 'resize_linear', target_h, target_w, True, f'{t_resize:.4f}', '', 0, 'baseline linear resize'])

        # crop
        t0 = time.perf_counter()
        crop_img = center_crop(im, target_h, target_w)
        t_crop = time.perf_counter() - t0
        io.imsave(str(case_dir / 'crop.png'), crop_img)
        metrics_rows.append([run_id, image_name, 'crop', target_h, target_w, True, f'{t_crop:.4f}', '', 0, 'center crop baseline'])

        # seam width only
        t0 = time.perf_counter()
        seam_width_img = seam_carve_image(im, (h, target_w))
        t_sw = time.perf_counter() - t0
        print(f'  seam_width done in {t_sw:.3f}s')
        io.imsave(str(case_dir / 'seam_width.png'), seam_width_img)
        metrics_rows.append([run_id, image_name, 'seam_width', h, target_w, True, f'{t_sw:.4f}', '', 0, 'vertical seam only'])

        # seam height only
        t0 = time.perf_counter()
        seam_height_img = seam_carve_image(im, (target_h, w))
        t_sh = time.perf_counter() - t0
        print(f'  seam_height done in {t_sh:.3f}s')
        io.imsave(str(case_dir / 'seam_height.png'), seam_height_img)
        metrics_rows.append([run_id, image_name, 'seam_height', target_h, w, True, f'{t_sh:.4f}', '', 0, 'transpose reuse'])

        grid_items = [
            ('original', im),
            ('resize_linear', resize_img),
            ('crop', crop_img),
            ('seam_width', seam_width_img),
            ('seam_height', seam_height_img),
        ]
        save_compare_grid(str(case_dir / 'compare_grid.png'), grid_items)

    metrics_path = repo_root / 'metrics' / 'hw1_op1_metrics.csv'
    with metrics_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'run_id',
            'image_name',
            'method',
            'target_h',
            'target_w',
            'success',
            'runtime_s',
            'error_type',
            'fix_rounds',
            'notes',
        ])
        writer.writerows(metrics_rows)

    print(f'Outputs saved to: {output_root}')
    print(f'Metrics saved to: {metrics_path}')


if __name__ == '__main__':
    main()

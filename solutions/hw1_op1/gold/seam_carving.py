from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
from scipy import ndimage
from skimage import io


LAPLACIAN_KERNEL = np.array([[0.5, 1.0, 0.5], [1.0, -6.0, 1.0], [0.5, 1.0, 0.5]], dtype=np.float64)


def compute_energy(im):
    """Compute per-pixel energy using the Laplacian-style kernel from the assignment."""
    im_f = im.astype(np.float64)
    if im_f.ndim == 2:
        return ndimage.convolve(im_f, LAPLACIAN_KERNEL, mode='reflect') ** 2

    energy = np.zeros(im_f.shape[:2], dtype=np.float64)
    for c in range(im_f.shape[2]):
        lap = ndimage.convolve(im_f[:, :, c], LAPLACIAN_KERNEL, mode='reflect')
        energy += lap ** 2
    return energy


def build_cumulative_cost(energy):
    """Dynamic programming table and backtrack pointers for vertical seams."""
    h, w = energy.shape
    dp = np.zeros((h, w), dtype=np.float64)
    backtrack = np.zeros((h, w), dtype=np.int32)
    dp[0] = energy[0]

    for i in range(1, h):
        for j in range(w):
            left = max(j - 1, 0)
            right = min(j + 1, w - 1)
            prev_slice = dp[i - 1, left:right + 1]
            best_offset = int(np.argmin(prev_slice))
            best_prev = left + best_offset
            dp[i, j] = energy[i, j] + dp[i - 1, best_prev]
            backtrack[i, j] = best_prev

    return dp, backtrack


def find_vertical_seam(energy):
    """Find the minimum-energy vertical seam."""
    h, w = energy.shape
    dp, backtrack = build_cumulative_cost(energy)

    seam = np.zeros(h, dtype=np.int32)
    seam[h - 1] = int(np.argmin(dp[h - 1]))
    for i in range(h - 2, -1, -1):
        seam[i] = backtrack[i + 1, seam[i + 1]]

    # Keep this assertion during early-stage debugging to catch invalid seams.
    if h > 1:
        assert np.all(np.abs(np.diff(seam)) <= 1), 'Backtracked seam is not continuous.'
    assert np.all((seam >= 0) & (seam < w)), 'Seam index out of bounds.'
    return seam


def remove_vertical_seam(im, seam):
    """Remove one vertical seam from RGB/gray image."""
    h, w = im.shape[:2]
    assert seam.shape[0] == h, 'Seam length must equal image height.'

    if im.ndim == 3:
        mask = np.ones((h, w), dtype=bool)
        mask[np.arange(h), seam] = False
        out = im[mask].reshape((h, w - 1, im.shape[2]))
    else:
        mask = np.ones((h, w), dtype=bool)
        mask[np.arange(h), seam] = False
        out = im[mask].reshape((h, w - 1))

    assert out.shape[1] == w - 1, 'Width must decrease by exactly 1 after seam removal.'
    return out


def seam_overlay(im, seam):
    """Draw seam on top of image for debugging visualization."""
    vis = im.copy()
    if vis.ndim == 2:
        vis = np.stack([vis, vis, vis], axis=2)
    vis[np.arange(vis.shape[0]), seam] = np.array([255, 0, 0], dtype=vis.dtype)
    return vis


def carve_width_only(im, target_w):
    """Width-only seam carving. Recompute energy after every seam removal."""
    h, w = im.shape[:2]
    target_w = max(1, int(target_w))
    if target_w >= w:
        return im.copy()

    out = im.copy()
    for _ in range(w - target_w):
        energy = compute_energy(out)
        seam = find_vertical_seam(energy)
        out = remove_vertical_seam(out, seam)
    return out


def carve_height_only(im, target_h):
    """Height shrink by transpose-reusing vertical seam logic."""
    target_h = max(1, int(target_h))
    h, _ = im.shape[:2]
    if target_h >= h:
        return im.copy()

    if im.ndim == 3:
        transposed = np.transpose(im, (1, 0, 2))
        carved_t = carve_width_only(transposed, target_h)
        return np.transpose(carved_t, (1, 0, 2))

    transposed = np.transpose(im, (1, 0))
    carved_t = carve_width_only(transposed, target_h)
    return np.transpose(carved_t, (1, 0))


def export_first_working_outputs(input_image, output_dir):
    """Export the required stage outputs for width-only first working version."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    im = io.imread(str(input_image))
    if im.ndim == 3 and im.shape[2] == 4:
        im = im[:, :, :3]

    energy = compute_energy(im)
    e_min, e_max = float(np.min(energy)), float(np.max(energy))
    energy_norm = np.zeros_like(energy, dtype=np.float64)
    if e_max > e_min:
        energy_norm = (energy - e_min) / (e_max - e_min)
    plt.imsave(str(output_dir / 'energy_map.png'), energy_norm, cmap='magma')

    seam = find_vertical_seam(energy)
    io.imsave(str(output_dir / 'seam_overlay.png'), seam_overlay(im, seam))

    im_minus_1 = remove_vertical_seam(im, seam)
    io.imsave(str(output_dir / 'remove_1_seam.png'), im_minus_1)

    im_minus_10 = im.copy()
    steps = min(10, max(0, im.shape[1] - 1))
    for _ in range(steps):
        e = compute_energy(im_minus_10)
        s = find_vertical_seam(e)
        im_minus_10 = remove_vertical_seam(im_minus_10, s)
    io.imsave(str(output_dir / 'remove_10_seams.png'), im_minus_10)

    target_w = max(1, int(im.shape[1] * 0.6))
    im_target = carve_width_only(im, target_w)
    io.imsave(str(output_dir / 'remove_to_target_width.png'), im_target)


def seam_carve_image(im, sz):
    """Seam carving to resize image to target size.

    Args:
        im: (h, w, 3) input RGB image (uint8)
        sz: (target_h, target_w) target size

    Returns:
        resized image of shape (target_h, target_w, 3)
    """
    h, w = im.shape[:2]
    target_h, target_w = int(sz[0]), int(sz[1])
    if target_w > w or target_h > h:
        raise ValueError('Current version supports shrinking only (target_h <= h and target_w <= w).')

    out = carve_width_only(im, target_w)
    out = carve_height_only(out, target_h)
    return out


def main():
    """Launch the provided GUI entrypoint."""
    im = io.imread('../figs/original.png')
    if im.ndim == 3 and im.shape[2] == 4:
        im = im[:, :, :3]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.subplots_adjust(bottom=0.22)
    ax1.imshow(im)
    ax1.set_title('Input image')
    ax1.axis('off')
    himg = ax2.imshow(np.zeros_like(im))
    ax2.set_title('Resized Image\nAdjust sliders and click the button')
    ax2.axis('off')

    slider_col_ax = fig.add_axes([0.15, 0.10, 0.30, 0.03])
    slider_row_ax = fig.add_axes([0.15, 0.05, 0.30, 0.03])
    slider_col = Slider(slider_col_ax, 'Col scale', 0.5, 2.0, valinit=1.0)
    slider_row = Slider(slider_row_ax, 'Row scale', 0.5, 2.0, valinit=1.0)

    btn_ax = fig.add_axes([0.60, 0.06, 0.20, 0.06])
    btn = Button(btn_ax, 'Seam Carving', color='lightblue', hovercolor='deepskyblue')

    def on_click(event):
        del event
        h, w = im.shape[:2]
        target_w = min(w, max(1, int(w * slider_col.val)))
        target_h = min(h, max(1, int(h * slider_row.val)))
        result = seam_carve_image(im, (target_h, target_w))
        himg.set_data(result)
        himg.set_extent([0, result.shape[1], result.shape[0], 0])
        ax2.set_title(f'Resized Image ({result.shape[0]}x{result.shape[1]})')
        fig.canvas.draw_idle()

    btn.on_clicked(on_click)
    plt.show()


if __name__ == '__main__':
    main()

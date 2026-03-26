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

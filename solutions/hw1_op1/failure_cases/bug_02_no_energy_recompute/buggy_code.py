import numpy as np


def carve_width_buggy(im, target_w, compute_energy, find_vertical_seam, remove_vertical_seam):
    """Bug: compute energy only once, then reuse stale energy after seam removal."""
    h, w = im.shape[:2]
    if target_w >= w:
        return im.copy()

    out = im.copy()
    energy = compute_energy(out)  # BUG: should be recomputed every iteration.
    for _ in range(w - target_w):
        seam = find_vertical_seam(energy)
        out = remove_vertical_seam(out, seam)
    return out

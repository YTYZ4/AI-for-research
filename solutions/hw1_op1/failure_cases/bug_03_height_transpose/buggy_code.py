import numpy as np


def carve_height_buggy(im, target_h, carve_width_only):
    """Bug: wrong transpose order for color image causes channel/layout mismatch."""
    h, _ = im.shape[:2]
    if target_h >= h:
        return im.copy()

    # BUG: should be (1, 0, 2). This swaps channel into width dimension.
    transposed = np.transpose(im, (2, 0, 1))
    carved = carve_width_only(transposed, target_h)
    # BUG: inverse transpose also mismatched.
    out = np.transpose(carved, (1, 2, 0))
    return out

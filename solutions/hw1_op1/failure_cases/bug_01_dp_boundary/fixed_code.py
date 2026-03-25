import numpy as np


def build_cumulative_cost_fixed(energy):
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

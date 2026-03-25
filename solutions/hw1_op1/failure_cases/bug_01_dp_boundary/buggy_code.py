import numpy as np


def build_cumulative_cost_buggy(energy):
    """Bug: no boundary clamp, will index out of range at j=0 and j=w-1."""
    h, w = energy.shape
    dp = np.zeros((h, w), dtype=np.float64)
    backtrack = np.zeros((h, w), dtype=np.int32)
    dp[0] = energy[0]

    for i in range(1, h):
        for j in range(w):
            # BUG: left/right can go out of bounds in Python indexing logic.
            prev = [dp[i - 1, j - 1], dp[i - 1, j], dp[i - 1, j + 1]]
            best_offset = int(np.argmin(prev)) - 1
            backtrack[i, j] = j + best_offset
            dp[i, j] = energy[i, j] + prev[best_offset + 1]

    return dp, backtrack

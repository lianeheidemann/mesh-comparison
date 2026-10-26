import numpy as np
from scipy.spatial import cKDTree


def maybe_subsample(points, max_points=50000, seed=0):
    if len(points) <= max_points:
        return points
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(points), size=max_points, replace=False)
    return points[idx]


def nn_distances(src_points, dst_points):
    tree = cKDTree(dst_points)
    dists, idx = tree.query(src_points, k=1, workers=-1)
    return dists, idx


def symmetric_mse(points_a, points_b):
    """Mean of the two directional mean squared nearest-neighbour distances between two point sets."""
    d_ab, _ = nn_distances(points_a, points_b)
    d_ba, _ = nn_distances(points_b, points_a)
    return 0.5 * (np.mean(d_ab ** 2) + np.mean(d_ba ** 2))

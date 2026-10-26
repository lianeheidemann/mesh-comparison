import itertools

import numpy as np

from .distances import maybe_subsample, nn_distances


def to_o3d_pcd(points):
    import open3d as o3d

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
    return pcd


def axis_rotations():
    """The 24 rotations that map the coordinate axes onto each other (signed permutation matrices, det = +1).
    Any orientation lies within about 63 degrees of one of them, and axis-convention changes (y-up vs z-up, flips)
    are among them exactly."""
    rotations = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1.0, -1.0), repeat=3):
            matrix = np.zeros((3, 3))
            matrix[np.arange(3), perm] = signs
            if np.linalg.det(matrix) > 0:
                rotations.append(matrix)
    return rotations


def principal_axis_rotations(src_pts, tgt_pts):
    """The 4 proper rotations that map the principal axes of ``src`` onto those of ``tgt`` (one per sign choice
    with det = +1). Principal axes rotate with the object, so for a rotated copy one of them is the rotation."""
    def axes(points):
        _, vectors = np.linalg.eigh(np.cov((points - points.mean(axis=0)).T))
        return vectors[:, ::-1]  # largest variance first

    src_axes, tgt_axes = axes(src_pts), axes(tgt_pts)
    rotations = []
    for signs in itertools.product((1.0, -1.0), repeat=3):
        rotation = tgt_axes @ np.diag(signs) @ src_axes.T
        if np.linalg.det(rotation) > 0:
            rotations.append(rotation)
    return rotations


def initial_similarity(src_pts, tgt_pts, rotation=np.eye(3)):
    """Similarity that rotates ``src`` about its centroid, scales it to the RMS radius of ``tgt`` (a scale estimate
    that does not depend on the orientation) and moves its centroid onto the centroid of ``tgt``."""
    src_center = src_pts.mean(axis=0)
    tgt_center = tgt_pts.mean(axis=0)
    src_radius = np.sqrt(np.mean(np.sum((src_pts - src_center) ** 2, axis=1))) + 1e-12
    tgt_radius = np.sqrt(np.mean(np.sum((tgt_pts - tgt_center) ** 2, axis=1))) + 1e-12
    s = tgt_radius / src_radius

    T = np.eye(4, dtype=np.float64)
    T[:3, :3] = s * rotation
    T[:3, 3] = tgt_center - s * rotation @ src_center
    return T


def _symmetric_mean_distance(src_pts, tgt_pts, transform):
    moved = src_pts @ transform[:3, :3].T + transform[:3, 3]
    d_src, _ = nn_distances(moved, tgt_pts)
    d_tgt, _ = nn_distances(tgt_pts, moved)
    return 0.5 * (np.mean(d_src) + np.mean(d_tgt))


def similarity_icp_align(rm_points, gt_points,
                         coarse_dist=0.25,
                         fine_dist=0.05,
                         max_points=50000,
                         max_iter=100,
                         select_points=5000,
                         select_iter=30):
    """
    Similarity ICP (rotation + translation + uniform scale) with a global start. A short coarse ICP
    (``select_iter`` iterations on ``select_points`` samples) is run from 28 starts: the 24 axis rotations and the
    4 principal-axis rotations. The start whose result has the smallest symmetric mean nearest-neighbour distance is
    kept, and the coarse and fine ICP are then run from it on ``max_points`` samples.
    """
    import open3d as o3d

    est = o3d.pipelines.registration.TransformationEstimationPointToPoint(with_scaling=True)
    criteria = o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=max_iter)
    select_criteria = o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=select_iter)

    rm_sel = maybe_subsample(rm_points, max_points=select_points, seed=3)
    gt_sel = maybe_subsample(gt_points, max_points=select_points, seed=4)
    src_sel, tgt_sel = to_o3d_pcd(rm_sel), to_o3d_pcd(gt_sel)
    best_start, best_score = None, np.inf
    for rotation in axis_rotations() + principal_axis_rotations(rm_sel, gt_sel):
        start = initial_similarity(rm_sel, gt_sel, rotation)
        coarse = o3d.pipelines.registration.registration_icp(src_sel, tgt_sel, coarse_dist, start, est,
                                                             select_criteria)
        score = _symmetric_mean_distance(rm_sel, gt_sel, coarse.transformation)
        if score < best_score:
            best_start, best_score = coarse.transformation, score

    rm_pts = maybe_subsample(rm_points, max_points=max_points, seed=1)
    gt_pts = maybe_subsample(gt_points, max_points=max_points, seed=2)
    src, tgt = to_o3d_pcd(rm_pts), to_o3d_pcd(gt_pts)
    coarse = o3d.pipelines.registration.registration_icp(src, tgt, coarse_dist, best_start, est, criteria)
    fine = o3d.pipelines.registration.registration_icp(src, tgt, fine_dist, coarse.transformation, est, criteria)

    return fine.transformation, fine.fitness, fine.inlier_rmse

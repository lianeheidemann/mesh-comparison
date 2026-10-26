# Surface-sample metrics of the evaluation-v2 protocol (Chamfer, HD95, F-score), split by input-view regions.
"""
evaluation-v2 geometric metrics (contracts CC-14 to CC-17, ADR 0001).

The legacy vertex-to-vertex metrics of ``metrics.py`` stay unchanged. Here both surfaces are sampled uniformly by
area with fixed seeds, and the metrics are computed on those samples in the normalized space (GT bounding-box
diagonal = 1), so every distance and every tolerance ``tau`` is a fraction of the GT diagonal.
"""
import numpy as np

from ..common.distances import nn_distances

PROTOCOL = "evaluation-v2"
N_SAMPLES = 100_000
SEED_GT = 0
SEED_RM = 1
TAUS = (0.01, 0.02, 0.05)
HD_PERCENTILE = 95
REGIONS = ("all", "visible", "hidden")


def sample_surface(mesh, n, seed):
    """``n`` points drawn uniformly over the surface of ``mesh`` (faces chosen by area, uniform barycentrics)."""
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces)
    if len(faces) == 0:
        raise ValueError("Mesh has no faces; surface sampling needs a triangle mesh.")
    tri = vertices[faces]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    total = areas.sum()
    if not np.isfinite(total) or total <= 0:
        raise ValueError("Mesh has zero surface area; surface sampling is not possible.")

    rng = np.random.default_rng(seed)
    face_idx = rng.choice(len(faces), size=n, p=areas / total)
    r1 = np.sqrt(rng.random(n))
    r2 = rng.random(n)
    a, b, c = tri[face_idx, 0], tri[face_idx, 1], tri[face_idx, 2]
    return (1.0 - r1)[:, None] * a + (r1 * (1.0 - r2))[:, None] * b + (r1 * r2)[:, None] * c


def icp_scale(transform):
    """Uniform scale factor applied by the similarity ICP (1 when alignment did not run)."""
    return float(np.cbrt(np.linalg.det(np.asarray(transform)[:3, :3])))


def _region_metrics(d_gt2rm, d_rm2gt, taus):
    """CD, HD95 and precision/recall/F-score per tau for one set of directional distances (NaN when empty)."""
    row = {}
    if len(d_gt2rm) == 0 or len(d_rm2gt) == 0:
        row["chamfer_mean"] = np.nan
        row["hd95"] = np.nan
    else:
        row["chamfer_mean"] = 0.5 * (np.mean(d_gt2rm) + np.mean(d_rm2gt))
        row["hd95"] = max(np.percentile(d_gt2rm, HD_PERCENTILE), np.percentile(d_rm2gt, HD_PERCENTILE))
    for tau in taus:
        precision = np.mean(d_rm2gt < tau) if len(d_rm2gt) else np.nan  # RM samples close to the GT
        recall = np.mean(d_gt2rm < tau) if len(d_gt2rm) else np.nan  # GT samples covered by the RM
        if np.isnan(precision) or np.isnan(recall):
            fscore = np.nan
        elif precision + recall > 0:
            fscore = 2.0 * precision * recall / (precision + recall)
        else:
            fscore = 0.0
        key = tau_key(tau)
        row[f"precision_{key}"] = precision
        row[f"recall_{key}"] = recall
        row[f"fscore_{key}"] = fscore
    return row


def tau_key(tau):
    """Column suffix of a tolerance: 0.01 -> ``tau1pct``."""
    return f"tau{tau * 100:g}pct"


def compute_metrics_v2(gt_points, rm_points, taus=TAUS, gt_visible=None):
    """
    Metrics per region on surface samples: ``{"all": {...}, "visible": {...}, "hidden": {...}}``.

    ``gt_visible`` (bool per GT sample) splits the GT samples by visibility from the input view; each RM sample
    takes the region of its nearest GT sample. Without it only ``"all"`` is returned.
    """
    d_gt2rm, _ = nn_distances(gt_points, rm_points)
    d_rm2gt, nearest_gt = nn_distances(rm_points, gt_points)

    results = {"all": {"gt_fraction": 1.0, **_region_metrics(d_gt2rm, d_rm2gt, taus)}}
    if gt_visible is not None:
        gt_visible = np.asarray(gt_visible, dtype=bool)
        rm_visible = gt_visible[nearest_gt]
        for region, gt_sel, rm_sel in (("visible", gt_visible, rm_visible), ("hidden", ~gt_visible, ~rm_visible)):
            results[region] = {"gt_fraction": float(np.mean(gt_sel)),
                               **_region_metrics(d_gt2rm[gt_sel], d_rm2gt[rm_sel], taus)}
    return results

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
CURVE_TAUS = np.round(np.arange(1, 21) * 0.005, 3)  # F(tau) curve: 0.5 % to 10 % of the GT diagonal
HD_PERCENTILE = 95
REGIONS = ("all", "visible", "hidden")


def sample_surface(mesh, n, seed, return_normals=False):
    """``n`` points drawn uniformly over the surface of ``mesh`` (faces chosen by area, uniform barycentrics).

    With ``return_normals`` also returns the unit normal of the face of each point (the random draws, and so the
    points, are the same either way)."""
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces)
    if len(faces) == 0:
        raise ValueError("Mesh has no faces; surface sampling needs a triangle mesh.")
    tri = vertices[faces]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    total = areas.sum()
    if not np.isfinite(total) or total <= 0:
        raise ValueError("Mesh has zero surface area; surface sampling is not possible.")

    rng = np.random.default_rng(seed)
    face_idx = rng.choice(len(faces), size=n, p=areas / total)
    r1 = np.sqrt(rng.random(n))
    r2 = rng.random(n)
    a, b, c = tri[face_idx, 0], tri[face_idx, 1], tri[face_idx, 2]
    points = (1.0 - r1)[:, None] * a + (r1 * (1.0 - r2))[:, None] * b + (r1 * r2)[:, None] * c
    if not return_normals:
        return points
    normals = cross[face_idx] / (2.0 * areas[face_idx])[:, None]  # only faces with area > 0 are ever drawn
    return points, normals


def icp_scale(transform):
    """Uniform scale factor applied by the similarity ICP (1 when alignment did not run)."""
    return float(np.cbrt(np.linalg.det(np.asarray(transform)[:3, :3])))


def _prf(d_gt2rm, d_rm2gt, tau):
    """Precision (RM samples within ``tau`` of the GT), recall (GT samples within ``tau`` of the RM) and F-score."""
    precision = np.mean(d_rm2gt < tau) if len(d_rm2gt) else np.nan
    recall = np.mean(d_gt2rm < tau) if len(d_gt2rm) else np.nan
    if np.isnan(precision) or np.isnan(recall):
        fscore = np.nan
    elif precision + recall > 0:
        fscore = 2.0 * precision * recall / (precision + recall)
    else:
        fscore = 0.0
    return precision, recall, fscore


def fscore_curve(d_gt2rm, d_rm2gt, taus=CURVE_TAUS):
    """``(taus, precision, recall, fscore)`` arrays over a grid of tolerances."""
    taus = np.asarray(taus, dtype=np.float64)
    values = np.array([_prf(d_gt2rm, d_rm2gt, tau) for tau in taus], dtype=np.float64).reshape(len(taus), 3)
    return taus, values[:, 0], values[:, 1], values[:, 2]


def fscore_auc(taus, fscores):
    """Area under F(tau) by the trapezoid rule, divided by the tau range: in [0, 1], 1 for a perfect match."""
    taus = np.asarray(taus, dtype=np.float64)
    fscores = np.asarray(fscores, dtype=np.float64)
    if np.any(np.isnan(fscores)):
        return np.nan
    return float(np.sum(0.5 * (fscores[1:] + fscores[:-1]) * np.diff(taus)) / (taus[-1] - taus[0]))


def normal_consistency(gt_normals, rm_normals_at_gt, rm_normals, gt_normals_at_rm):
    """Mean |cos| between each sample's unit normal and the normal of its nearest sample on the other surface,
    averaged over both directions (``*_at_*``: normals of the nearest neighbours, row-aligned). Absolute value
    because reconstructed meshes are not reliably oriented. In [0, 1], higher is better; NaN if a side is empty."""
    if len(gt_normals) == 0 or len(rm_normals) == 0:
        return np.nan
    gt_side = np.abs(np.sum(gt_normals * rm_normals_at_gt, axis=1))
    rm_side = np.abs(np.sum(rm_normals * gt_normals_at_rm, axis=1))
    return float(0.5 * (np.mean(gt_side) + np.mean(rm_side)))


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
        precision, recall, fscore = _prf(d_gt2rm, d_rm2gt, tau)
        key = tau_key(tau)
        row[f"precision_{key}"] = precision
        row[f"recall_{key}"] = recall
        row[f"fscore_{key}"] = fscore
    return row


def tau_key(tau):
    """Column suffix of a tolerance: 0.01 -> ``tau1pct``."""
    return f"tau{tau * 100:g}pct"


def compute_metrics_v2(gt_points, rm_points, taus=TAUS, gt_visible=None, gt_normals=None, rm_normals=None,
                       curve_taus=CURVE_TAUS):
    """
    Metrics per region on surface samples: ``{"all": {...}, "visible": {...}, "hidden": {...}}``.

    ``gt_visible`` (bool per GT sample) splits the GT samples by visibility from the input view; each RM sample
    takes the region of its nearest GT sample. Without it only ``"all"`` is returned. Each region also holds its
    F(tau) curve over ``curve_taus`` (``"curve"``), the area under it (``"fscore_auc"``) and, when both normal
    arrays are given, ``"normal_consistency"`` (NaN otherwise).
    """
    d_gt2rm, nearest_rm = nn_distances(gt_points, rm_points)
    d_rm2gt, nearest_gt = nn_distances(rm_points, gt_points)
    with_normals = gt_normals is not None and rm_normals is not None

    def region(gt_sel, rm_sel, gt_fraction):
        row = {"gt_fraction": gt_fraction, **_region_metrics(d_gt2rm[gt_sel], d_rm2gt[rm_sel], taus)}
        curve = fscore_curve(d_gt2rm[gt_sel], d_rm2gt[rm_sel], curve_taus)
        row["curve"] = curve
        row["fscore_auc"] = fscore_auc(curve[0], curve[3])
        row["normal_consistency"] = np.nan
        if with_normals:
            row["normal_consistency"] = normal_consistency(
                gt_normals[gt_sel], rm_normals[nearest_rm[gt_sel]], rm_normals[rm_sel], gt_normals[nearest_gt[rm_sel]])
        return row

    everything_gt = np.ones(len(gt_points), dtype=bool)
    everything_rm = np.ones(len(rm_points), dtype=bool)
    results = {"all": region(everything_gt, everything_rm, 1.0)}
    if gt_visible is not None:
        gt_visible = np.asarray(gt_visible, dtype=bool)
        rm_visible = gt_visible[nearest_gt]
        for name, gt_sel, rm_sel in (("visible", gt_visible, rm_visible), ("hidden", ~gt_visible, ~rm_visible)):
            results[name] = region(gt_sel, rm_sel, float(np.mean(gt_sel)))
    return results

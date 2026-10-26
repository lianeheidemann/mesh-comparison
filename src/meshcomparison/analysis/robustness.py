# Controlled mesh perturbations and metric evaluation for the invariance/sensitivity study (ADR 0002).
"""
Metric-validation study, not part of the GUI pipelines.

Perturbations are applied to a GT that is already normalized (bounding-box diagonal 1, as in the pipelines), so
every intensity is a fraction of the GT diagonal. Besides the package metrics, a vertex-to-vertex baseline is
computed for comparison (the earlier metric definition, kept here only as a reference). Pairs are compared
**without ICP**: the study isolates how each metric responds to a known change, not how registration behaves.
All randomness uses fixed seeds.
"""
import numpy as np
import pandas as pd
import trimesh

from ..common.alignment import similarity_icp_align
from ..common.distances import nn_distances, symmetric_surface_mse
from ..common.sampling import N_SAMPLES, SEED_GT, SEED_RM, sample_surface
from ..geometry.metrics import TAUS, compute_metrics, icp_scale, tau_key
from ..perceptual.image_metrics import crop_to_union_mask, masked_lpips, masked_psnr, masked_ssim, summarize_stats


def normalized(mesh):
    """Copy of ``mesh`` scaled so its bounding-box diagonal is 1 (the scale used by the pipelines)."""
    out = mesh.copy()
    out.apply_scale(1.0 / np.linalg.norm(out.bounds[1] - out.bounds[0]))
    return out


def _mesh(vertices, faces):
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def subdivide(mesh, iterations=1, face_mask=None):
    """Midpoint subdivision: the surface is unchanged, only the triangulation gets finer. With ``face_mask`` only
    those faces are subdivided at each iteration (uneven vertex density over the same surface)."""
    vertices, faces = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    for _ in range(iterations):
        index = None
        if face_mask is not None:
            centroids = vertices[faces].mean(axis=1)
            index = np.flatnonzero(face_mask(centroids))
        vertices, faces = trimesh.remesh.subdivide(vertices, faces, face_index=index)
    return _mesh(vertices, faces)


def densify(mesh, min_vertices):
    """Subdivide until the mesh has at least ``min_vertices`` vertices (so local perturbations are resolved)."""
    while len(mesh.vertices) < min_vertices:
        mesh = subdivide(mesh)
    return mesh


def half_subdivided(mesh, iterations=2):
    """Same surface, with the half of the faces on the low-x side subdivided ``iterations`` times."""
    middle = float(np.median(np.asarray(mesh.vertices)[:, 0]))
    return subdivide(mesh, iterations, face_mask=lambda c: c[:, 0] < middle)


def permute_vertices(mesh, seed=0):
    """Same mesh with the vertex order shuffled (faces re-indexed, face order kept)."""
    order = np.random.default_rng(seed).permutation(len(mesh.vertices))
    inverse = np.empty_like(order)
    inverse[order] = np.arange(len(order))
    return _mesh(np.asarray(mesh.vertices)[order], inverse[np.asarray(mesh.faces)])


def _vertex_normals(mesh):
    return np.asarray(_mesh(mesh.vertices, mesh.faces).vertex_normals)


def normal_noise(mesh, sigma, seed=0):
    """Each vertex moved along its normal by a Gaussian amount of standard deviation ``sigma``."""
    offsets = np.random.default_rng(seed).normal(0.0, sigma, len(mesh.vertices))
    return _mesh(np.asarray(mesh.vertices) + offsets[:, None] * _vertex_normals(mesh), mesh.faces)


def _anchor(mesh):
    """Fixed reference point on the surface: the vertex with the largest x (ties broken by index)."""
    return np.asarray(mesh.vertices)[int(np.argmax(np.asarray(mesh.vertices)[:, 0]))]


def local_bump(mesh, amplitude, radius=0.1):
    """Gaussian bump of height ``amplitude`` along the vertex normals, centred on the anchor vertex."""
    vertices = np.asarray(mesh.vertices)
    weight = np.exp(-np.sum((vertices - _anchor(mesh)) ** 2, axis=1) / (2.0 * radius ** 2))
    return _mesh(vertices + amplitude * weight[:, None] * _vertex_normals(mesh), mesh.faces)


def remove_region(mesh, fraction):
    """Remove the faces closest to the anchor until ``fraction`` of the surface area is gone (incompleteness)."""
    if fraction <= 0:
        return mesh.copy()
    faces = np.asarray(mesh.faces)
    centroids = np.asarray(mesh.vertices)[faces].mean(axis=1)
    order = np.argsort(np.linalg.norm(centroids - _anchor(mesh), axis=1), kind="stable")
    area = np.asarray(mesh.area_faces)[order]
    removed = order[np.cumsum(area) <= fraction * area.sum()]
    keep = np.ones(len(faces), dtype=bool)
    keep[removed] = False
    out = _mesh(mesh.vertices, faces[keep])
    out.remove_unreferenced_vertices()
    return out


PERTURBATIONS = {  # name -> (function(mesh, intensity), intensities, unit)
    "normal_noise": (normal_noise, (0.0, 0.0025, 0.005, 0.01, 0.02), "sigma (fraction of GT diagonal)"),
    "local_bump": (local_bump, (0.0, 0.01, 0.025, 0.05, 0.1), "bump height (fraction of GT diagonal)"),
    "remove_region": (remove_region, (0.0, 0.05, 0.1, 0.2, 0.3), "fraction of the GT surface removed"),
}


def vertex_baseline(gt_vertices, rm_vertices):
    """Vertex-to-nearest-vertex Chamfer (mean), symmetric Hausdorff and RMSE: the baseline the surface metrics
    are compared against (it depends on the triangulation, which is what the invariance study shows)."""
    d_gt2rm, _ = nn_distances(gt_vertices, rm_vertices)
    d_rm2gt, _ = nn_distances(rm_vertices, gt_vertices)
    return {
        "vertex_chamfer": 0.5 * (np.mean(d_gt2rm) + np.mean(d_rm2gt)),
        "vertex_hausdorff": max(np.max(d_gt2rm), np.max(d_rm2gt)),
        "vertex_rmse": np.sqrt(0.5 * (np.mean(d_gt2rm ** 2) + np.mean(d_rm2gt ** 2))),
    }


def geometric_metrics(gt, rm, n_samples=N_SAMPLES):
    """Vertex baseline and surface-sample metrics of ``rm`` against ``gt`` (no ICP)."""
    gt_points, gt_normals = sample_surface(gt, n_samples, SEED_GT, return_normals=True)
    rm_points, rm_normals = sample_surface(rm, n_samples, SEED_RM, return_normals=True)
    m = compute_metrics(gt_points, rm_points, TAUS, gt_normals=gt_normals, rm_normals=rm_normals,
                        gt_mesh=gt, rm_mesh=rm)["all"]
    row = {
        **vertex_baseline(np.asarray(gt.vertices), np.asarray(rm.vertices)),
        "chamfer": m["chamfer_mean"],
        "hd95": m["hd95"],
    }
    for tau in TAUS:
        row[f"fscore_{tau_key(tau)}"] = m[f"fscore_{tau_key(tau)}"]
    row["fscore_auc"] = m["fscore_auc"]
    row["normal_consistency"] = m["normal_consistency"]
    return row


def perceptual_metrics(gt, rm, num_views=8, width=320, height=240, elevation_deg=25.264, lpips_model=None,
                       device="cpu"):
    """Mean over finite values (as in the perceptual summary) of PSNR, SSIM and LPIPS (NaN without a model) over
    ``num_views`` views, with the cameras, masks and crops of the perceptual pipeline."""
    from ..perceptual.cameras import make_view_renderer
    from ..perceptual.pipeline import _render_view, _scene_framing

    azimuths = np.linspace(0.0, 360.0, num_views, endpoint=False)
    center, diag = _scene_framing([gt, rm])
    values = {"psnr": [], "ssim": [], "lpips": []}
    with make_view_renderer(gt, rm, width=width, height=height) as renderer:
        for azimuth in azimuths:
            view = _render_view(renderer, gt, rm, azimuth, center, diag, elevation_deg, 1.45, 1.05)
            gt_crop, rm_crop, _, _, union = crop_to_union_mask(
                view["gt_img"], view["rm_img"], view["gt_mask"], view["rm_mask"], pad=12)
            gt_masked = gt_crop * union[..., None].astype(np.float32)
            rm_masked = rm_crop * union[..., None].astype(np.float32)
            values["psnr"].append(masked_psnr(gt_crop, rm_crop, union))
            values["ssim"].append(masked_ssim(gt_masked, rm_masked))
            values["lpips"].append(
                masked_lpips(lpips_model, gt_masked, rm_masked, device) if lpips_model is not None else np.nan)
    return {f"perceptual_{name}": summarize_stats(v)["mean"] for name, v in values.items()}


SAMPLING_SIZES = (1_000, 3_000, 10_000, 30_000, 100_000, 300_000)


def sampling_uncertainty(gt, rm, sizes=SAMPLING_SIZES, n_seeds=5, taus=TAUS):
    """Monte Carlo spread of the surface metrics: one row per (samples per mesh, seed pair), each pair drawing
    independent GT/RM samples (seeds ``2k`` and ``2k + 1``). Shows how far a single run's value can move."""
    rows = []
    for n in sizes:
        for k in range(n_seeds):
            gt_points, gt_normals = sample_surface(gt, n, 2 * k, return_normals=True)
            rm_points, rm_normals = sample_surface(rm, n, 2 * k + 1, return_normals=True)
            m = compute_metrics(gt_points, rm_points, taus, gt_normals=gt_normals, rm_normals=rm_normals,
                                gt_mesh=gt, rm_mesh=rm)["all"]
            row = {"n_samples": n, "seed_pair": k, "chamfer": m["chamfer_mean"], "hd95": m["hd95"],
                   "fscore_auc": m["fscore_auc"], "normal_consistency": m["normal_consistency"]}
            row.update({f"fscore_{tau_key(t)}": m[f"fscore_{tau_key(t)}"] for t in taus})
            rows.append(row)
    return pd.DataFrame(rows)


def similarity_transform(angle_deg, axis=(0.0, 0.0, 1.0), scale=1.0, translation=(0.0, 0.0, 0.0)):
    """4 x 4 matrix of ``x -> scale * R(axis, angle) x + translation`` (rotation about the origin)."""
    transform = trimesh.transformations.rotation_matrix(np.deg2rad(angle_deg), np.asarray(axis, dtype=np.float64))
    transform[:3, :3] *= scale
    transform[:3, 3] = translation
    return transform


def icp_recovery(gt, applied, mse_threshold=1e-4, n_samples=N_SAMPLES):
    """Apply the known similarity ``applied`` to the normalized ``gt`` to build the RM, align it back exactly as
    ``common/prepare.py`` does, and report how well the inverse was recovered: rotation error (degrees), relative
    scale error, translation error and the post-alignment surface metrics (ideal: 0, 0, 0 and Chamfer 0, F 1)."""
    rm = gt.copy()
    rm.apply_transform(applied)
    gt_points, gt_normals = sample_surface(gt, n_samples, SEED_GT, return_normals=True)
    rm_points = sample_surface(rm, n_samples, SEED_RM)
    pre_mse = symmetric_surface_mse(gt_points, rm_points, gt, rm)
    triggered = pre_mse > mse_threshold
    recovered = np.eye(4)
    if triggered:
        recovered, _, _ = similarity_icp_align(rm_points, gt_points)
    rm_aligned = rm.copy()
    rm_aligned.apply_transform(recovered)

    residual = recovered @ applied  # identity when the alignment undoes the applied transform
    residual_scale = icp_scale(residual)
    rotation = residual[:3, :3] / residual_scale
    cos_angle = np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0)
    rm_points_aligned, rm_normals = sample_surface(rm_aligned, n_samples, SEED_RM, return_normals=True)
    m = compute_metrics(gt_points, rm_points_aligned, TAUS, gt_normals=gt_normals, rm_normals=rm_normals,
                        gt_mesh=gt, rm_mesh=rm_aligned)["all"]
    return {
        "pre_alignment_mse": pre_mse,
        "alignment_triggered": bool(triggered),
        "rotation_error_deg": float(np.degrees(np.arccos(cos_angle))),
        "scale_error": residual_scale - 1.0,
        "translation_error": float(np.linalg.norm(residual[:3, 3])),
        "icp_scale": icp_scale(recovered),
        "chamfer": m["chamfer_mean"],
        "hd95": m["hd95"],
        "fscore_tau1pct": m["fscore_tau1pct"],
    }

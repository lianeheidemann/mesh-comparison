import os

import pandas as pd

from ..common.io import ensure_dirs
from ..common.prepare import export_aligned, prepare_meshes, transform_columns
from .heatmap import colorize_gt_heatmap, save_heatmap_figure
from .metrics import compute_metrics
from .metrics_v2 import (
    N_SAMPLES, PROTOCOL, REGIONS, SEED_GT, SEED_RM, TAUS, compute_metrics_v2, icp_scale, sample_surface, tau_key,
)
from .rendering import build_shared_camera, render_mesh
from .visibility import gt_visibility

TOTAL_STEPS = 7

OUTPUT_SUBDIRS = {
    "renders": ("renders",),
    "heatmaps": ("heatmaps",),
    "metrics": ("metrics",),
    "aligned": ("aligned",),
}


def _render_views_and_heatmap(prepared, d_gt2rm, paths, azimuth_deg, elevation_deg, width, height):
    """Orthographic GT/RM renders from one shared camera, plus the GT deviation heatmap (mesh and figure)."""
    gt, rm_aligned = prepared.gt, prepared.rm_aligned
    cam_cfg = build_shared_camera([gt, rm_aligned], azimuth_deg=azimuth_deg, elevation_deg=elevation_deg)

    files = {
        "gt_render": os.path.join(paths["renders"], "gt_ortho.png"),
        "rm_render": os.path.join(paths["renders"], "rm_aligned_ortho.png"),
        "heat_mesh": os.path.join(paths["heatmaps"], "gt_heatmap_colored.ply"),
        "heat_image": os.path.join(paths["heatmaps"], "gt_heatmap_ortho.png"),
    }
    heat_image_tmp = os.path.join(paths["heatmaps"], "_gt_heatmap_render_tmp.png")

    render_mesh(gt, files["gt_render"], cam_cfg, width=width, height=height)
    render_mesh(rm_aligned, files["rm_render"], cam_cfg, width=width, height=height)

    heat_mesh, norm, cmap = colorize_gt_heatmap(gt, d_gt2rm)
    heat_mesh.export(files["heat_mesh"])

    heat_rgba = render_mesh(heat_mesh, heat_image_tmp, cam_cfg, width=width, height=height)
    save_heatmap_figure(heat_rgba, files["heat_image"], norm, cmap, label="GT vertex distance to aligned RM")
    if os.path.exists(heat_image_tmp):
        os.remove(heat_image_tmp)

    return files


def _metrics_row(gt_path, rm_path, prepared, post_mse_norm, metrics, mse_threshold_normalized,
                 azimuth_deg, elevation_deg):
    diag = prepared.gt_diag_raw
    return {
        "gt_file": os.path.abspath(gt_path),
        "rm_file": os.path.abspath(rm_path),

        "alignment_triggered": prepared.alignment_triggered,
        "mse_threshold_normalized": mse_threshold_normalized,

        "pre_alignment_mse_normalized": prepared.pre_mse_norm,
        "post_alignment_mse_normalized": post_mse_norm,

        "pre_alignment_mse_gt_units_sq": prepared.pre_mse_norm * (diag ** 2),
        "post_alignment_mse_gt_units_sq": post_mse_norm * (diag ** 2),

        "mean_chamfer_normalized": metrics["chamfer_mean"],
        "symmetric_hausdorff_normalized": metrics["hausdorff"],
        "symmetric_rmse_normalized": metrics["rmse"],

        "mean_chamfer_gt_units": metrics["chamfer_mean"] * diag,
        "symmetric_hausdorff_gt_units": metrics["hausdorff"] * diag,
        "symmetric_rmse_gt_units": metrics["rmse"] * diag,

        "gt_bbox_diagonal_original_units": diag,
        "camera_azimuth_deg": azimuth_deg,
        "camera_elevation_deg": elevation_deg,
        **transform_columns(prepared.final_transform),
    }


def _compute_v2(prepared, input_azimuth_deg, input_elevation_deg):
    """evaluation-v2 metrics on surface samples of the normalized GT and aligned RM (regions need the input view)."""
    gt_points, gt_normals = sample_surface(prepared.gt, N_SAMPLES, SEED_GT, return_normals=True)
    rm_points, rm_normals = sample_surface(prepared.rm_aligned, N_SAMPLES, SEED_RM, return_normals=True)
    gt_visible = None
    if input_azimuth_deg is not None and input_elevation_deg is not None:
        gt_visible = gt_visibility(prepared.gt, gt_points, input_azimuth_deg, input_elevation_deg)
    return compute_metrics_v2(gt_points, rm_points, TAUS, gt_visible, gt_normals, rm_normals)


def _v2_rows(prepared, results, input_azimuth_deg, input_elevation_deg):
    """One row per region of ``metrics_geometry_v2.csv``; distances also in GT units, F-score columns per tau."""
    diag = prepared.gt_diag_raw
    rows = []
    for region in REGIONS:
        if region not in results:
            continue
        m = results[region]
        row = {
            "protocol": PROTOCOL,
            "region": region,
            "gt_surface_fraction": m["gt_fraction"],
            "chamfer_mean_normalized": m["chamfer_mean"],
            "chamfer_mean_gt_units": m["chamfer_mean"] * diag,
            "hd95_normalized": m["hd95"],
            "hd95_gt_units": m["hd95"] * diag,
        }
        for tau in TAUS:
            key = tau_key(tau)
            row[f"precision_{key}"] = m[f"precision_{key}"]
            row[f"recall_{key}"] = m[f"recall_{key}"]
            row[f"fscore_{key}"] = m[f"fscore_{key}"]
        row.update({
            "n_samples": N_SAMPLES,
            "seed_gt": SEED_GT,
            "seed_rm": SEED_RM,
            "input_azimuth_deg": input_azimuth_deg,
            "input_elevation_deg": input_elevation_deg,
            "alignment_triggered": prepared.alignment_triggered,
            "icp_scale": icp_scale(prepared.final_transform),
            "gt_bbox_diagonal_original_units": diag,
            # added after the first evaluation-v2 columns (ADR 0002)
            "normal_consistency": m["normal_consistency"],
            "fscore_auc": m["fscore_auc"],
        })
        rows.append(row)
    return rows


def _curve_rows(results):
    """Long-format F(tau) curve per region for ``fscore_curve_v2.csv`` (tau as a fraction of the GT diagonal)."""
    rows = []
    for region in REGIONS:
        if region not in results:
            continue
        for tau, precision, recall, fscore in zip(*results[region]["curve"]):
            rows.append({"protocol": PROTOCOL, "region": region, "tau_normalized": tau,
                         "precision": precision, "recall": recall, "fscore": fscore})
    return rows


def run_pipeline(gt_path, rm_path, out_dir,
                 mse_threshold_normalized=1e-4,
                 azimuth_deg=45.0,
                 elevation_deg=35.264,
                 width=1600,
                 height=1200,
                 input_azimuth_deg=None,
                 input_elevation_deg=None):
    """``input_azimuth_deg``/``input_elevation_deg``: view of the input image in the GT frame (z up); when given,
    the evaluation-v2 metrics are also split into GT regions visible and hidden from that view."""
    paths = ensure_dirs(out_dir, OUTPUT_SUBDIRS)

    prepared = prepare_meshes(gt_path, rm_path, mse_threshold_normalized, TOTAL_STEPS)

    print(f"[5/{TOTAL_STEPS}] Computing final metrics...")
    metrics = compute_metrics(prepared.gt.vertices, prepared.rm_aligned.vertices)
    post_mse_norm = metrics["mse"]  # same distances, computed once
    v2_results = _compute_v2(prepared, input_azimuth_deg, input_elevation_deg)

    print(f"[6/{TOTAL_STEPS}] Rendering orthographic views and heatmap...")
    files = _render_views_and_heatmap(
        prepared, metrics["d_gt2rm"], paths, azimuth_deg, elevation_deg, width, height)

    print(f"[7/{TOTAL_STEPS}] Saving outputs...")
    aligned_path = export_aligned(prepared, paths["aligned"])

    csv_path = os.path.join(paths["metrics"], "metrics_geometry.csv")
    pd.DataFrame([_metrics_row(gt_path, rm_path, prepared, post_mse_norm, metrics, mse_threshold_normalized,
                               azimuth_deg, elevation_deg)]).to_csv(csv_path, index=False)
    v2_csv_path = os.path.join(paths["metrics"], "metrics_geometry_v2.csv")
    pd.DataFrame(_v2_rows(prepared, v2_results, input_azimuth_deg, input_elevation_deg)).to_csv(
        v2_csv_path, index=False)
    curve_csv_path = os.path.join(paths["metrics"], "fscore_curve_v2.csv")
    pd.DataFrame(_curve_rows(v2_results)).to_csv(curve_csv_path, index=False)

    print("\nDone.")
    print(f"GT render:        {files['gt_render']}")
    print(f"RM render:        {files['rm_render']}")
    print(f"Heatmap image:    {files['heat_image']}")
    print(f"Heatmap mesh:     {files['heat_mesh']}")
    print(f"Aligned RM mesh:  {aligned_path}")
    print(f"Metrics CSV:      {csv_path}")
    print(f"Metrics v2 CSV:   {v2_csv_path}")
    print(f"F(tau) curve CSV: {curve_csv_path}")

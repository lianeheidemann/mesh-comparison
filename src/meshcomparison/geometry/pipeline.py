import os

import numpy as np
import pandas as pd

from ..common.alignment import similarity_icp_align
from ..common.distances import symmetric_mse
from ..common.io import ensure_dirs, load_mesh
from ..common.provenance import collect_provenance
from .heatmap import colorize_gt_heatmap, save_heatmap_figure
from .metrics import compute_metrics
from .rendering import build_shared_camera, render_mesh

OUTPUT_SUBDIRS = {
    "renders": ("renders",),
    "heatmaps": ("heatmaps",),
    "metrics": ("metrics",),
    "aligned": ("aligned",),
}


def run_pipeline(gt_path, rm_path, out_dir,
                 mse_threshold_normalized=1e-4,
                 azimuth_deg=45.0,
                 elevation_deg=35.264,
                 width=1600,
                 height=1200):
    paths = ensure_dirs(out_dir, OUTPUT_SUBDIRS)

    print("[1/7] Loading meshes...")
    gt_raw = load_mesh(gt_path)
    rm_raw = load_mesh(rm_path)

    print("[2/7] Internal scale normalization...")
    gt = gt_raw.copy()
    rm = rm_raw.copy()

    gt_diag_raw = np.linalg.norm(gt.bounds[1] - gt.bounds[0])
    if gt_diag_raw < 1e-12:
        raise ValueError("GT mesh bounding-box diagonal is too small.")

    internal_scale = 1.0 / gt_diag_raw
    gt.apply_scale(internal_scale)
    rm.apply_scale(internal_scale)

    print("[3/7] Computing pre-alignment MSE...")
    pre_mse_norm = symmetric_mse(gt.vertices, rm.vertices)
    alignment_triggered = pre_mse_norm > mse_threshold_normalized

    print(f"    Pre-alignment symmetric MSE (normalized): {pre_mse_norm:.8e}")
    print(f"    Threshold (normalized): {mse_threshold_normalized:.8e}")
    print(f"    Alignment triggered: {alignment_triggered}")

    rm_aligned = rm.copy()
    final_transform = np.eye(4)

    if alignment_triggered:
        print("[4/7] Running similarity ICP alignment (RM -> GT)...")
        T, fitness, inlier_rmse = similarity_icp_align(
            rm.vertices,
            gt.vertices
        )
        rm_aligned.apply_transform(T)
        final_transform = T
        print(f"    ICP fitness: {fitness:.6f}")
        print(f"    ICP inlier RMSE: {inlier_rmse:.6f}")
    else:
        print("[4/7] Alignment skipped.")

    print("[5/7] Computing final metrics...")
    post_mse_norm = symmetric_mse(gt.vertices, rm_aligned.vertices)
    metrics = compute_metrics(gt.vertices, rm_aligned.vertices)

    chamfer_gt_units = metrics["chamfer_mean"] * gt_diag_raw
    hausdorff_gt_units = metrics["hausdorff"] * gt_diag_raw
    rmse_gt_units = metrics["rmse"] * gt_diag_raw

    pre_mse_gt_units_sq = pre_mse_norm * (gt_diag_raw ** 2)
    post_mse_gt_units_sq = post_mse_norm * (gt_diag_raw ** 2)

    print("[6/7] Rendering orthographic views and heatmap...")
    cam_cfg = build_shared_camera(
        [gt, rm_aligned],
        azimuth_deg=azimuth_deg,
        elevation_deg=elevation_deg
    )

    gt_render_path = os.path.join(paths["renders"], "gt_ortho.png")
    rm_render_path = os.path.join(paths["renders"], "rm_aligned_ortho.png")

    render_mesh(gt, gt_render_path, cam_cfg, width=width, height=height)
    render_mesh(rm_aligned, rm_render_path, cam_cfg, width=width, height=height)

    heat_mesh, norm, cmap = colorize_gt_heatmap(gt, metrics["d_gt2rm"])
    heat_mesh_path = os.path.join(paths["heatmaps"], "gt_heatmap_colored.ply")
    heat_img_tmp = os.path.join(paths["heatmaps"], "_gt_heatmap_render_tmp.png")
    heat_img_final = os.path.join(paths["heatmaps"], "gt_heatmap_ortho.png")

    heat_mesh.export(heat_mesh_path)

    heat_rgba = render_mesh(heat_mesh, heat_img_tmp, cam_cfg, width=width, height=height)
    save_heatmap_figure(
        heat_rgba,
        heat_img_final,
        norm,
        cmap,
        label="GT vertex distance to aligned RM"
    )

    if os.path.exists(heat_img_tmp):
        os.remove(heat_img_tmp)

    print("[7/7] Saving outputs...")

    rm_aligned_export = rm_aligned.copy()
    rm_aligned_export.apply_scale(1.0 / internal_scale)
    aligned_path = os.path.join(paths["aligned"], "rm_aligned.ply")
    rm_aligned_export.export(aligned_path)

    df = pd.DataFrame([{
        "gt_file": os.path.abspath(gt_path),
        "rm_file": os.path.abspath(rm_path),

        "alignment_triggered": alignment_triggered,
        "mse_threshold_normalized": mse_threshold_normalized,

        "pre_alignment_mse_normalized": pre_mse_norm,
        "post_alignment_mse_normalized": post_mse_norm,

        "pre_alignment_mse_gt_units_sq": pre_mse_gt_units_sq,
        "post_alignment_mse_gt_units_sq": post_mse_gt_units_sq,

        "mean_chamfer_normalized": metrics["chamfer_mean"],
        "symmetric_hausdorff_normalized": metrics["hausdorff"],
        "symmetric_rmse_normalized": metrics["rmse"],

        "mean_chamfer_gt_units": chamfer_gt_units,
        "symmetric_hausdorff_gt_units": hausdorff_gt_units,
        "symmetric_rmse_gt_units": rmse_gt_units,

        "gt_bbox_diagonal_original_units": gt_diag_raw,
        "camera_azimuth_deg": azimuth_deg,
        "camera_elevation_deg": elevation_deg,
        "final_transform_00": final_transform[0, 0],
        "final_transform_01": final_transform[0, 1],
        "final_transform_02": final_transform[0, 2],
        "final_transform_03": final_transform[0, 3],
        "final_transform_10": final_transform[1, 0],
        "final_transform_11": final_transform[1, 1],
        "final_transform_12": final_transform[1, 2],
        "final_transform_13": final_transform[1, 3],
        "final_transform_20": final_transform[2, 0],
        "final_transform_21": final_transform[2, 1],
        "final_transform_22": final_transform[2, 2],
        "final_transform_23": final_transform[2, 3],
    }])

    csv_path = os.path.join(paths["metrics"], "metrics_geometry.csv")
    df.to_csv(csv_path, index=False)

    meta_csv = os.path.join(paths["metrics"], "run_metadata_geometry.csv")
    pd.DataFrame([{
        "gt_file": os.path.abspath(gt_path),
        "rm_file": os.path.abspath(rm_path),
        "mse_threshold_normalized": mse_threshold_normalized,
        "camera_azimuth_deg": azimuth_deg,
        "camera_elevation_deg": elevation_deg,
        "render_width": width,
        "render_height": height,
        "heatmap_vmax_normalized": float(norm.vmax),
        "heatmap_vmax_gt_units": float(norm.vmax * gt_diag_raw),
        **collect_provenance(),
    }]).to_csv(meta_csv, index=False)

    print("\nDone.")
    print(f"GT render:        {gt_render_path}")
    print(f"RM render:        {rm_render_path}")
    print(f"Heatmap image:    {heat_img_final}")
    print(f"Heatmap mesh:     {heat_mesh_path}")
    print(f"Aligned RM mesh:  {aligned_path}")
    print(f"Metrics CSV:      {csv_path}")

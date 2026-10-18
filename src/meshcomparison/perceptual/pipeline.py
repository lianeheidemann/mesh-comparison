import os

import imageio.v2 as imageio
import numpy as np
import pandas as pd

from ..common.alignment import similarity_icp_align
from ..common.device import get_device_info
from ..common.distances import symmetric_mse
from ..common.io import ensure_dirs, load_mesh
from .cameras import build_tight_ortho_camera, camera_pose_for_view, render_mesh_rgba
from .figures import save_pair_figure
from .image_metrics import (
    crop_to_union_mask,
    masked_lpips,
    masked_psnr,
    masked_ssim,
    rgba_to_rgb_mask,
    summarize_stats,
)

OUTPUT_SUBDIRS = {
    "renders_gt": ("renders", "gt"),
    "renders_rm": ("renders", "rm"),
    "renders_pairs": ("renders", "pairs"),
    "metrics": ("metrics",),
    "aligned": ("aligned",),
}


def run_pipeline(gt_path, rm_path, out_dir,
                 mse_threshold_normalized=1e-4,
                 elevation_deg=25.264,
                 width=1600,
                 height=1200,
                 num_views=100,
                 save_views=(1, 33, 66),
                 camera_margin=1.05,
                 radius_factor=1.45,
                 device="auto"):

    paths = ensure_dirs(out_dir, OUTPUT_SUBDIRS)

    print("[1/8] Loading meshes...")
    gt_raw = load_mesh(gt_path)
    rm_raw = load_mesh(rm_path)

    print("[2/8] Internal scale normalization...")
    gt = gt_raw.copy()
    rm = rm_raw.copy()

    gt_diag_raw = np.linalg.norm(gt.bounds[1] - gt.bounds[0])
    if gt_diag_raw < 1e-12:
        raise ValueError("GT mesh bounding-box diagonal is too small.")

    internal_scale = 1.0 / gt_diag_raw
    gt.apply_scale(internal_scale)
    rm.apply_scale(internal_scale)

    print("[3/8] Computing pre-alignment MSE...")
    pre_mse_norm = symmetric_mse(gt.vertices, rm.vertices)
    alignment_triggered = pre_mse_norm > mse_threshold_normalized

    print(f"    Pre-alignment symmetric MSE (normalized): {pre_mse_norm:.8e}")
    print(f"    Threshold (normalized): {mse_threshold_normalized:.8e}")
    print(f"    Alignment triggered: {alignment_triggered}")

    rm_aligned = rm.copy()
    final_transform = np.eye(4)

    if alignment_triggered:
        print("[4/8] Running similarity ICP alignment (RM -> GT)...")
        T, fitness, inlier_rmse = similarity_icp_align(
            rm.vertices,
            gt.vertices
        )
        rm_aligned.apply_transform(T)
        final_transform = T
        print(f"    ICP fitness: {fitness:.6f}")
        print(f"    ICP inlier RMSE: {inlier_rmse:.6f}")
    else:
        print("[4/8] Alignment skipped.")

    print("[5/8] Preparing LPIPS model...")
    import lpips

    device_info = get_device_info(device)
    device = device_info.device
    if device_info.warning:
        print(f"    WARNING: {device_info.warning}")
    try:
        lpips_model = lpips.LPIPS(net="alex").to(device).eval()
    except Exception as e:
        raise RuntimeError(
            "LPIPS could not be initialized. Make sure it is installed:\n"
            "pip install lpips torch torchvision\n"
            f"Original error: {e}"
        )
    print(f"    LPIPS device: {device_info.describe()}")

    print("[6/8] Rendering 100 views and computing metrics...")
    per_view_rows = []
    save_views = set(save_views)
    azimuths = np.linspace(0.0, 360.0, num_views, endpoint=False)

    lpips_vals = []
    psnr_vals = []
    ssim_vals = []

    all_meshes = [gt, rm_aligned]
    center = 0.5 * (np.vstack([m.vertices for m in all_meshes]).min(axis=0) +
                    np.vstack([m.vertices for m in all_meshes]).max(axis=0))
    diag = np.linalg.norm(np.vstack([m.vertices for m in all_meshes]).max(axis=0) -
                          np.vstack([m.vertices for m in all_meshes]).min(axis=0)) + 1e-12

    for i, az in enumerate(azimuths, start=1):
        cam_pose = camera_pose_for_view(
            center=center,
            diag=diag,
            azimuth_deg=az,
            elevation_deg=elevation_deg,
            radius_factor=radius_factor
        )

        cam_cfg = build_tight_ortho_camera(
            [gt, rm_aligned],
            camera_pose=cam_pose,
            margin=camera_margin
        )

        gt_rgba = render_mesh_rgba(
            gt, cam_cfg, width=width, height=height
        )
        rm_rgba = render_mesh_rgba(
            rm_aligned, cam_cfg, width=width, height=height
        )

        gt_img, gt_alpha, gt_mask = rgba_to_rgb_mask(gt_rgba)
        rm_img, rm_alpha, rm_mask = rgba_to_rgb_mask(rm_rgba)

        # Crop to union of object regions so background does not dominate
        gt_crop, rm_crop, gt_mask_c, rm_mask_c, union_c = crop_to_union_mask(
            gt_img, rm_img, gt_mask, rm_mask, pad=12
        )

        # Zero background in the crop
        gt_crop_masked = gt_crop * union_c[..., None].astype(np.float32)
        rm_crop_masked = rm_crop * union_c[..., None].astype(np.float32)

        psnr_val = masked_psnr(gt_crop, rm_crop, union_c)
        ssim_val = masked_ssim(gt_crop_masked, rm_crop_masked)
        lpips_val = masked_lpips(lpips_model, gt_crop_masked, rm_crop_masked, device=device)

        lpips_vals.append(lpips_val)
        psnr_vals.append(psnr_val)
        ssim_vals.append(ssim_val)

        per_view_rows.append({
            "view_idx": i,
            "azimuth_deg": float(az),
            "elevation_deg": float(elevation_deg),
            "lpips": lpips_val,
            "psnr": psnr_val,
            "ssim": ssim_val,
            "crop_h": int(gt_crop.shape[0]),
            "crop_w": int(gt_crop.shape[1]),
            "xmag": float(cam_cfg["xmag"]),
            "ymag": float(cam_cfg["ymag"]),
        })

        if i in save_views:
            gt_save = os.path.join(paths["renders_gt"], f"gt_view{i:03d}.png")
            rm_save = os.path.join(paths["renders_rm"], f"rm_view{i:03d}.png")
            pair_save = os.path.join(paths["renders_pairs"], f"pair_view{i:03d}.png")

            imageio.imwrite(gt_save, (gt_img * 255).astype(np.uint8))
            imageio.imwrite(rm_save, (rm_img * 255).astype(np.uint8))
            save_pair_figure(gt_img, rm_img, pair_save, title_left=f"GT view {i}", title_right=f"RM view {i}")

            print(f"    Saved selected view {i:03d}")

        print(
            f"    View {i:03d}/{num_views} | az={az:7.2f} | "
            f"LPIPS={lpips_val:.5f} | PSNR={psnr_val:.3f} | SSIM={ssim_val:.5f}"
        )

    print("[7/8] Summarizing metrics...")

    lpips_stats = summarize_stats(lpips_vals)
    psnr_stats = summarize_stats(psnr_vals)
    ssim_stats = summarize_stats(ssim_vals)

    summary_rows = []
    for metric_name, stats in [
        ("lpips", lpips_stats),
        ("psnr", psnr_stats),
        ("ssim", ssim_stats),
    ]:
        summary_rows.append({
            "metric": metric_name,
            "min": stats["min"],
            "max": stats["max"],
            "p25": stats["p25"],
            "p75": stats["p75"],
            "median": stats["median"],
            "mean": stats["mean"],
        })

    per_view_df = pd.DataFrame(per_view_rows)
    summary_df = pd.DataFrame(summary_rows)

    per_view_csv = os.path.join(paths["metrics"], "per_view_metrics.csv")
    summary_csv = os.path.join(paths["metrics"], "metrics_perceptual.csv")
    per_view_df.to_csv(per_view_csv, index=False)
    summary_df.to_csv(summary_csv, index=False)

    print("[8/8] Saving aligned mesh and metadata...")

    rm_aligned_export = rm_aligned.copy()
    rm_aligned_export.apply_scale(1.0 / internal_scale)
    aligned_path = os.path.join(paths["aligned"], "rm_aligned.ply")
    rm_aligned_export.export(aligned_path)

    meta_df = pd.DataFrame([{
        "gt_file": os.path.abspath(gt_path),
        "rm_file": os.path.abspath(rm_path),
        "alignment_triggered": alignment_triggered,
        "mse_threshold_normalized": mse_threshold_normalized,
        "pre_alignment_mse_normalized": pre_mse_norm,
        "gt_bbox_diagonal_original_units": gt_diag_raw,
        "camera_elevation_deg": elevation_deg,
        "num_views": num_views,
        "saved_views": ",".join(map(str, sorted(save_views))),
        "camera_margin": camera_margin,
        "radius_factor": radius_factor,
        "lpips_device": device_info.describe(),
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
    meta_csv = os.path.join(paths["metrics"], "run_metadata.csv")
    meta_df.to_csv(meta_csv, index=False)

    print("\nDone.")
    print(f"GT renders:       {paths['renders_gt']}")
    print(f"RM renders:       {paths['renders_rm']}")
    print(f"Pair renders:     {paths['renders_pairs']}")
    print(f"Aligned RM mesh:  {aligned_path}")
    print(f"Per-view metrics: {per_view_csv}")
    print(f"Summary metrics:  {summary_csv}")
    print(f"Run metadata:     {meta_csv}")

    print("\nMetric summary:")
    print(summary_df.to_string(index=False))

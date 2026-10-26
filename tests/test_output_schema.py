import subprocess
import sys
from pathlib import Path

import pandas as pd

from meshcomparison.gui.config import RunConfig, build_commands

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"

TRANSFORM_COLUMNS = [f"final_transform_{r}{c}" for r in range(3) for c in range(4)]
TAU_COLUMNS = [f"{kind}_tau{t}pct" for t in (1, 2, 5) for kind in ("precision", "recall", "fscore")]
GEOMETRY_COLUMNS = [
    "region", "gt_surface_fraction", "chamfer_mean_normalized", "chamfer_mean_gt_units", "hd95_normalized",
    "hd95_gt_units", *TAU_COLUMNS, "fscore_auc", "normal_consistency",
    "gt_file", "rm_file", "alignment_triggered", "mse_threshold_normalized", "pre_alignment_mse_normalized",
    "post_alignment_mse_normalized", "icp_scale", "n_samples", "seed_gt", "seed_rm", "input_azimuth_deg",
    "input_elevation_deg", "camera_azimuth_deg", "camera_elevation_deg", "heatmap_vmax_gt_units",
    "gt_bbox_diagonal_original_units", *TRANSFORM_COLUMNS,
]
CURVE_COLUMNS = ["region", "tau_normalized", "precision", "recall", "fscore"]
PER_VIEW_COLUMNS = ["view_idx", "azimuth_deg", "elevation_deg", "lpips", "psnr", "ssim", "crop_h", "crop_w",
                    "xmag", "ymag"]
SUMMARY_COLUMNS = ["metric", "min", "max", "p25", "p75", "median", "mean"]
METADATA_COLUMNS = [
    "gt_file", "rm_file", "alignment_triggered", "mse_threshold_normalized", "pre_alignment_mse_normalized",
    "gt_bbox_diagonal_original_units", "camera_elevation_deg", "num_views", "saved_views", "camera_margin",
    "radius_factor", *TRANSFORM_COLUMNS,
]


def _run(cfg):
    python, commands = build_commands(cfg, python=sys.executable)
    for command in commands:
        result = subprocess.run([python, *command.args], input=command.stdin, text=True,
                                capture_output=True, timeout=600)
        assert result.returncode == 0, result.stderr


def _columns(path):
    return list(pd.read_csv(path).columns)


def test_geometric_outputs_schema(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_perceptual=False, width=320, height=240)
    _run(cfg)

    assert sorted(p.name for p in (tmp_path / "metrics").iterdir()) == ["fscore_curve.csv", "metrics_geometry.csv"]
    metrics = pd.read_csv(tmp_path / "metrics" / "metrics_geometry.csv")
    assert list(metrics.columns) == GEOMETRY_COLUMNS
    assert metrics["region"].tolist() == ["all"]  # no input view: whole surface only
    curve = pd.read_csv(tmp_path / "metrics" / "fscore_curve.csv")
    assert list(curve.columns) == CURVE_COLUMNS
    assert len(curve) == 20 and curve["fscore"].is_monotonic_increasing


def test_geometric_regions_with_input_view(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_perceptual=False, width=320, height=240, input_view=True, input_azimuth=-135.0,
                    input_elevation=25.264)
    _run(cfg)

    metrics = pd.read_csv(tmp_path / "metrics" / "metrics_geometry.csv").set_index("region")
    assert list(metrics.index) == ["all", "visible", "hidden"]
    assert metrics.loc["visible", "gt_surface_fraction"] + metrics.loc["hidden", "gt_surface_fraction"] == 1.0
    assert 0.0 < metrics.loc["visible", "gt_surface_fraction"] < 1.0


def test_perceptual_outputs_schema(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_geometry=False, width=320, height=240, num_views=2, save_views=(1, 2), device="cpu")
    _run(cfg)

    metrics = tmp_path / "metrics"
    names = ("metrics_perceptual.csv", "per_view_metrics.csv", "run_metadata.csv")
    assert sorted(p.name for p in metrics.iterdir()) == sorted(names)
    assert _columns(metrics / "per_view_metrics.csv") == PER_VIEW_COLUMNS
    assert _columns(metrics / "metrics_perceptual.csv") == SUMMARY_COLUMNS
    assert _columns(metrics / "run_metadata.csv") == METADATA_COLUMNS
    assert pd.read_csv(metrics / "metrics_perceptual.csv")["metric"].tolist() == ["lpips", "psnr", "ssim"]

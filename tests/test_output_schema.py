import subprocess
import sys
from pathlib import Path

import pandas as pd

from meshcomparison.gui.config import RunConfig, build_commands

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"
ORIGINAL = ROOT / "examples" / "output" / "metrics"  # record of a run of the original pipelines


def _run(cfg):
    python, commands = build_commands(cfg, python=sys.executable)
    for command in commands:
        result = subprocess.run([python, *command.args], input=command.stdin, text=True,
                                capture_output=True, timeout=600)
        assert result.returncode == 0, result.stderr


def _columns(path):
    return list(pd.read_csv(path).columns)


TAU_COLUMNS = [f"{kind}_tau{t}pct" for t in (1, 2, 5) for kind in ("precision", "recall", "fscore")]
GEOMETRY_V2_COLUMNS = [  # evaluation-v2 (ADR 0001), a separate file next to the legacy one
    "protocol", "region", "gt_surface_fraction", "chamfer_mean_normalized", "chamfer_mean_gt_units",
    "hd95_normalized", "hd95_gt_units", *TAU_COLUMNS, "n_samples", "seed_gt", "seed_rm", "input_azimuth_deg",
    "input_elevation_deg", "alignment_triggered", "icp_scale", "gt_bbox_diagonal_original_units",
]


def test_geometric_outputs_match_the_original_schema(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_perceptual=False, width=320, height=240)
    _run(cfg)

    # the original geometric CSV keeps its exact schema; evaluation-v2 writes its own file
    names = ["metrics_geometry.csv", "metrics_geometry_v2.csv"]
    assert sorted(p.name for p in (tmp_path / "metrics").iterdir()) == names
    assert _columns(tmp_path / "metrics" / "metrics_geometry.csv") == _columns(ORIGINAL / "metrics_geometry.csv")
    v2 = pd.read_csv(tmp_path / "metrics" / "metrics_geometry_v2.csv")
    assert list(v2.columns) == GEOMETRY_V2_COLUMNS
    assert v2["region"].tolist() == ["all"]  # no input view: whole surface only


def test_geometric_v2_regions_with_input_view(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_perceptual=False, width=320, height=240, input_view=True, input_azimuth=-135.0,
                    input_elevation=25.264)
    _run(cfg)

    v2 = pd.read_csv(tmp_path / "metrics" / "metrics_geometry_v2.csv").set_index("region")
    assert list(v2.index) == ["all", "visible", "hidden"]
    assert v2.loc["visible", "gt_surface_fraction"] + v2.loc["hidden", "gt_surface_fraction"] == 1.0
    assert 0.0 < v2.loc["visible", "gt_surface_fraction"] < 1.0


def test_perceptual_outputs_match_the_original_schema(tmp_path):
    cfg = RunConfig(gt=str(SAMPLES / "gt.stl"), rm=str(SAMPLES / "mod.stl"), out=str(tmp_path),
                    run_geometry=False, width=320, height=240, num_views=2, save_views=(1, 2), device="cpu")
    _run(cfg)

    names = ("metrics_perceptual.csv", "per_view_metrics.csv", "run_metadata.csv")
    assert sorted(p.name for p in (tmp_path / "metrics").iterdir()) == sorted(names)
    for name in ("metrics_perceptual.csv", "run_metadata.csv"):
        assert _columns(tmp_path / "metrics" / name) == _columns(ORIGINAL / name), name
    # per-view CSV: the legacy columns unchanged and in order, then the evaluation-v2 column
    assert _columns(tmp_path / "metrics" / "per_view_metrics.csv") == (
        _columns(ORIGINAL / "per_view_metrics.csv") + ["psnr_standard"])
    summary = pd.read_csv(tmp_path / "metrics" / "metrics_perceptual.csv")
    assert summary["metric"].tolist() == ["lpips", "psnr", "ssim", "psnr_standard"]

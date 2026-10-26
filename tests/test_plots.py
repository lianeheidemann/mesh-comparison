# Tests of the metric figures and of the estimates they show (bootstrap interval, sampling spread).
import numpy as np
import pandas as pd
import trimesh

from meshcomparison.analysis.plots import (
    bootstrap_mean_ci, plot_fscore_curve, plot_perceptual_views, plot_region_metrics, plot_sampling_uncertainty,
)
from meshcomparison.analysis.robustness import sampling_uncertainty


def test_bootstrap_interval_contains_the_mean_and_ignores_non_finite():
    values = [1.0, 2.0, 3.0, 4.0, np.inf, np.nan]
    mean, low, high = bootstrap_mean_ci(values, seed=1)
    assert mean == 2.5 and low <= mean <= high
    assert 1.0 <= low and high <= 4.0
    assert all(np.isnan(v) for v in bootstrap_mean_ci([np.nan, np.inf]))


def test_sampling_uncertainty_has_one_row_per_size_and_seed_pair():
    box = trimesh.creation.box()
    spread = sampling_uncertainty(box, box, sizes=(500, 2000), n_seeds=3)
    assert len(spread) == 6 and sorted(spread["n_samples"].unique()) == [500, 2000]
    # same surface: the Chamfer floor shrinks as the samples get denser
    means = spread.groupby("n_samples")["chamfer"].mean()
    assert means[2000] < means[500]


def test_figures_are_written(tmp_path):
    curve = pd.DataFrame({"region": ["all"] * 3, "tau_normalized": [0.01, 0.02, 0.03],
                          "precision": [0.8, 0.9, 1.0], "recall": [0.7, 0.9, 1.0], "fscore": [0.75, 0.9, 1.0]})
    metrics = pd.DataFrame([{
        "region": "all", "gt_surface_fraction": 1.0, "chamfer_mean_gt_units": 0.01, "hd95_gt_units": 0.05,
        "fscore_tau1pct": 0.9, "fscore_tau2pct": 0.95, "fscore_tau5pct": 0.99, "fscore_auc": 0.97,
        "normal_consistency": 0.93}])
    per_view = pd.DataFrame({"azimuth_deg": [0, 90, 180, 270], "psnr": [20.0, 21.0, np.inf, 19.0],
                             "ssim": [0.9, 0.92, 1.0, 0.88]})
    spread = pd.DataFrame({"n_samples": [100, 100, 1000, 1000], "seed_pair": [0, 1, 0, 1],
                           "chamfer": [0.02, 0.021, 0.01, 0.0101], "hd95": [0.05, 0.06, 0.04, 0.041],
                           "fscore_tau1pct": [0.5, 0.52, 0.8, 0.81], "normal_consistency": [0.8, 0.81, 0.9, 0.9]})
    paths = [
        plot_fscore_curve(curve, tmp_path / "curve.png"),
        plot_region_metrics(metrics, tmp_path / "regions.png"),
        plot_perceptual_views(per_view, tmp_path / "views.png", metrics=("lpips", "psnr", "ssim")),
        plot_sampling_uncertainty(spread, tmp_path / "spread.png"),
    ]
    for path in paths:
        assert path.is_file() and path.stat().st_size > 1000


def test_perceptual_figure_skips_missing_metrics(tmp_path):
    per_view = pd.DataFrame({"azimuth_deg": [0, 180], "ssim": [0.9, 0.8]})
    assert plot_perceptual_views(per_view, tmp_path / "v.png", metrics=("lpips", "ssim")).is_file()

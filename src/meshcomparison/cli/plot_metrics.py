# Command line: save the metric figures of a finished run (F(tau), regions, perceptual, sampling spread).
"""
Usage (from the repository root, after a run of the geometric and/or perceptual pipeline):

    python scripts/plot_metrics.py --run output [--figures output/figures] [--uncertainty]
                                   [--perceptual-metrics lpips,psnr,ssim]

Figures are written only for the CSVs present in ``<run>/metrics``. ``--uncertainty`` re-samples the GT and the
aligned RM (``<run>/aligned/rm_aligned.ply``) with several seeds and sample counts and also writes
``sampling_uncertainty.csv``.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

from ..analysis.plots import (
    plot_fscore_curve, plot_perceptual_views, plot_region_metrics, plot_sampling_uncertainty,
)
from ..analysis.robustness import sampling_uncertainty
from ..common.io import load_mesh


def _normalized_pair(metrics, run):
    """GT and aligned RM in the normalized space of the pipeline (both scaled by the GT diagonal)."""
    diag = float(metrics["gt_bbox_diagonal_original_units"].iloc[0])
    gt = load_mesh(metrics["gt_file"].iloc[0])
    rm = load_mesh(os.path.join(run, "aligned", "rm_aligned.ply"))
    gt.apply_scale(1.0 / diag)
    rm.apply_scale(1.0 / diag)
    return gt, rm


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True, help="output folder of a pipeline run")
    parser.add_argument("--figures", help="where to save the figures (default: <run>/figures)")
    parser.add_argument("--perceptual-metrics", default="lpips,psnr,ssim")
    parser.add_argument("--uncertainty", action="store_true", help="estimate the sampling spread (slower)")
    parser.add_argument("--seeds", type=int, default=5, help="seed pairs per sample count for --uncertainty")
    args = parser.parse_args(argv)

    metrics_dir = os.path.join(args.run, "metrics")
    figures = args.figures or os.path.join(args.run, "figures")
    os.makedirs(figures, exist_ok=True)
    written = []

    geometry_csv = os.path.join(metrics_dir, "metrics_geometry.csv")
    curve_csv = os.path.join(metrics_dir, "fscore_curve.csv")
    per_view_csv = os.path.join(metrics_dir, "per_view_metrics.csv")
    if os.path.isfile(curve_csv):
        written.append(plot_fscore_curve(pd.read_csv(curve_csv), os.path.join(figures, "fscore_curve.png")))
    if os.path.isfile(geometry_csv):
        metrics = pd.read_csv(geometry_csv)
        written.append(plot_region_metrics(metrics, os.path.join(figures, "geometric_metrics.png")))
        if args.uncertainty:
            spread = sampling_uncertainty(*_normalized_pair(metrics, args.run), n_seeds=args.seeds)
            spread.to_csv(os.path.join(figures, "sampling_uncertainty.csv"), index=False)
            written.append(plot_sampling_uncertainty(spread, os.path.join(figures, "sampling_uncertainty.png")))
            last = spread[spread["n_samples"] == spread["n_samples"].max()]
            cv = (last.std(numeric_only=True) / last.mean(numeric_only=True)).drop(["n_samples", "seed_pair"])
            print("Coefficient of variation at the largest sample count:")
            print(cv.replace([np.inf, -np.inf], np.nan).to_string(float_format=lambda v: f"{v:.2%}"))
    if os.path.isfile(per_view_csv):
        chosen = [m.strip() for m in args.perceptual_metrics.split(",") if m.strip()]
        written.append(plot_perceptual_views(pd.read_csv(per_view_csv), os.path.join(figures, "perceptual_views.png"),
                                             metrics=chosen))

    if not written:
        print(f"No metric CSVs found in {metrics_dir}", file=sys.stderr)
        return 1
    print("\n".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Command line: metric invariance and sensitivity study (ADR 0002) on one GT mesh.
"""
Usage (from the repository root, with offscreen OpenGL available for the perceptual columns):

    python scripts/robustness_study.py --gt data/samples/gt.stl --out output/robustness [--views 8] [--lpips]

Writes ``invariance.csv`` (same surface, different triangulations), ``sensitivity.csv`` (controlled
perturbations of increasing intensity), ``sensitivity.png`` and ``study_parameters.csv``.
"""
import argparse
import os
import platform
import sys

import numpy as np
import pandas as pd

from ..analysis.plots import plot_sensitivity
from ..analysis.robustness import DENSE_VERTICES, densify, invariance_rows, normalized, sensitivity_rows
from ..common.io import load_mesh
from ..common.sampling import N_SAMPLES, SEED_GT, SEED_RM


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--views", type=int, default=8, help="perceptual views per pair (0 = geometric only)")
    parser.add_argument("--lpips", action="store_true", help="also compute LPIPS (downloads AlexNet weights)")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    lpips_model, device = None, args.device
    if args.lpips:
        from ..perceptual.pipeline import _load_lpips

        lpips_model, device_info = _load_lpips(args.device)
        device = device_info.device

    gt = normalized(load_mesh(args.gt))
    print("[1/3] Invariance to the triangulation...")
    pd.DataFrame(invariance_rows(gt)).to_csv(os.path.join(args.out, "invariance.csv"), index=False)

    print("[2/3] Sensitivity to controlled perturbations...")
    base = densify(gt, DENSE_VERTICES)
    sensitivity = pd.DataFrame(sensitivity_rows(base, args.views, lpips_model, device))
    sensitivity.to_csv(os.path.join(args.out, "sensitivity.csv"), index=False)

    print("[3/3] Figure and parameters...")
    plot_sensitivity(sensitivity, os.path.join(args.out, "sensitivity.png"))
    pd.DataFrame([{
        "gt_file": os.path.abspath(args.gt), "base_vertices": len(base.vertices), "n_samples": N_SAMPLES,
        "seed_gt": SEED_GT, "seed_rm": SEED_RM, "perceptual_views": args.views, "lpips": bool(args.lpips),
        "icp": False, "python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(),
    }]).to_csv(os.path.join(args.out, "study_parameters.csv"), index=False)
    print(f"Done: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

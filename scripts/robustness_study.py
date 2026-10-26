# Runs the metric invariance and sensitivity study (ADR 0002) on one GT mesh and writes CSVs and figures.
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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from meshcomparison.analysis.robustness import (  # noqa: E402
    PERTURBATIONS, densify, geometric_metrics, half_subdivided, normalized, perceptual_metrics, permute_vertices,
    subdivide,
)
from meshcomparison.common.io import load_mesh  # noqa: E402
from meshcomparison.common.sampling import N_SAMPLES, SEED_GT, SEED_RM  # noqa: E402

DENSE_VERTICES = 20_000  # minimum vertex count of the base mesh used for the perturbations


def invariance_rows(gt):
    variants = {
        "identical copy": gt.copy(),
        "vertex order permuted": permute_vertices(gt, seed=0),
        "subdivided x1": subdivide(gt, 1),
        "subdivided x2": subdivide(gt, 2),
        "half subdivided x2 (uneven density)": half_subdivided(gt, 2),
    }
    rows = []
    for name, variant in variants.items():
        print(f"    invariance: {name} ({len(variant.vertices)} vertices)")
        rows.append({"variant": name, "rm_vertices": len(variant.vertices), **geometric_metrics(gt, variant)})
    return rows


def sensitivity_rows(base, views, lpips_model, device):
    rows = []
    for name, (perturb, intensities, unit) in PERTURBATIONS.items():
        for intensity in intensities:
            print(f"    sensitivity: {name} = {intensity}")
            rm = perturb(base, intensity)
            row = {"perturbation": name, "intensity": intensity, "unit": unit, **geometric_metrics(base, rm)}
            if views > 0:
                row.update(perceptual_metrics(base, rm, num_views=views, lpips_model=lpips_model, device=device))
            rows.append(row)
    return rows


PANELS = (  # (title, [(column, label)])
    ("Distances (lower is better)", [("vertex_chamfer", "Chamfer, vertex baseline"), ("chamfer", "Chamfer"),
                                     ("vertex_hausdorff", "Hausdorff, vertex baseline"), ("hd95", "HD95")]),
    ("Scores (higher is better)", [("fscore_tau1pct", "F@1%"), ("fscore_tau2pct", "F@2%"),
                                   ("fscore_auc", "AUC-F"), ("normal_consistency", "Normal consistency")]),
    ("Perceptual", [("perceptual_psnr", "PSNR (dB)"), ("perceptual_ssim", "SSIM"),
                    ("perceptual_lpips", "LPIPS")]),
)


def plot_sensitivity(df, path):
    panels = [p for p in PANELS if any(c in df and df[c].notna().any() for c, _ in p[1])]
    names = list(PERTURBATIONS)
    fig, axes = plt.subplots(len(names), len(panels), figsize=(4.2 * len(panels), 3.0 * len(names)), squeeze=False)
    for r, name in enumerate(names):
        sub = df[df["perturbation"] == name]
        for c, (title, series) in enumerate(panels):
            ax = axes[r, c]
            twin = None
            for k, (column, label) in enumerate(series):
                if column in sub and sub[column].notna().any():
                    target = ax
                    if "(dB)" not in label and any("(dB)" in other for _, other in series):
                        twin = twin or ax.twinx()  # unitless scores next to a dB curve get their own axis
                        target = twin
                    target.plot(sub["intensity"], sub[column], marker="o", label=label, color=f"C{k}")
            ax.set_xlabel(sub["unit"].iloc[0], fontsize=8)
            ax.set_title(f"{name}: {title}", fontsize=9)
            ax.grid(alpha=0.3)
            handles = [h for a in (ax, twin) if a is not None for h in a.get_legend_handles_labels()[0]]
            ax.legend(handles=handles, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


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
        from meshcomparison.perceptual.pipeline import _load_lpips

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

# Sweeps known rotations (with scale and translation) of a GT mesh and measures how well the ICP recovers them.
"""
Usage (from the repository root):

    python scripts/icp_study.py --gt data/samples/gt.stl --out output/icp [--step 15] [--scale 1.3]

Writes ``icp_recovery.csv`` (one row per axis and angle) and ``icp_recovery.png``.
"""
import argparse
import os
import sys

import pandas as pd

from meshcomparison.analysis.plots import plot_icp_recovery
from meshcomparison.analysis.robustness import icp_recovery, normalized, similarity_transform
from meshcomparison.common.io import load_mesh

AXES = {"z": (0.0, 0.0, 1.0), "[1,1,1]": (1.0, 1.0, 1.0)}
SUCCESS_CHAMFER = 0.01  # fraction of the GT diagonal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--step", type=float, default=15.0, help="angle step in degrees (0 to 180)")
    parser.add_argument("--scale", type=float, default=1.3, help="uniform scale applied to the RM")
    parser.add_argument("--shift", type=float, default=0.2, help="translation along x, fraction of the GT diagonal")
    args = parser.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    gt = normalized(load_mesh(args.gt))
    rows = []
    n_angles = int(round(180.0 / args.step)) + 1
    for axis_label, axis in AXES.items():
        for k in range(n_angles):
            angle = k * args.step
            applied = similarity_transform(angle, axis, args.scale, (args.shift, 0.0, 0.0))
            row = {"axis": axis_label, "angle_deg": angle, "scale": args.scale, "shift": args.shift,
                   **icp_recovery(gt, applied)}
            row["success"] = row["chamfer"] < SUCCESS_CHAMFER
            print(f"axis {axis_label:8s} angle {angle:6.1f} | rotation error {row['rotation_error_deg']:8.3f} deg | "
                  f"Chamfer {row['chamfer']:.2e} | success {row['success']}")
            rows.append(row)
    sweep = pd.DataFrame(rows)
    sweep.to_csv(os.path.join(args.out, "icp_recovery.csv"), index=False)
    plot_icp_recovery(sweep, os.path.join(args.out, "icp_recovery.png"), SUCCESS_CHAMFER)
    return 0


if __name__ == "__main__":
    sys.exit(main())

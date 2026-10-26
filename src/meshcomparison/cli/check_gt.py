# Command line: check candidate ground-truth meshes (and their manifest) and write a report.
"""
Usage (from the repository root):

    python scripts/check_gt.py <file or folder> [...] [--manifest gt/manifest.csv] [--cutoff 2025-06-01]
                               [--out gt_report.csv]

Each mesh gets OK / WARN / FAIL with the reasons (see docs/gt/README.md). With ``--manifest``, every row must name
an existing file, its source and its license; with ``--cutoff`` (the latest training-data date among the evaluated
models), objects published before that date are flagged as possibly seen in training. Exit code 1 if any FAIL.
"""
import argparse
import datetime
import os
import sys

import pandas as pd

from ..analysis.gt_check import check_file
from ..datasets.manifest import manifest_issues, mesh_files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="mesh files or folders (default: the files in the manifest)")
    parser.add_argument("--manifest", help="CSV with one row per GT (template: docs/gt/manifest_template.csv)")
    parser.add_argument("--cutoff", type=datetime.date.fromisoformat, help="training-data cutoff, YYYY-MM-DD")
    parser.add_argument("--out", default="gt_report.csv")
    args = parser.parse_args(argv)

    issues = manifest_issues(args.manifest, args.cutoff) if args.manifest else {}
    files = mesh_files(args.paths) if args.paths else [p for p in issues if os.path.isfile(p)]
    if not files and not issues:
        parser.error("give mesh files/folders or a manifest")

    rows = []
    for path in files:
        row = check_file(path)
        extra = issues.pop(os.path.normpath(os.path.abspath(path)), [])
        if extra:
            row["reasons"] = "; ".join(r for r in [row.get("reasons", "")] + extra if r)
            if row["status"] == "OK":
                row["status"] = "WARN"
        rows.append(row)
    for path, extra in issues.items():  # manifest rows whose file was not checked (missing or not requested)
        if "manifest: file not found" in extra:
            rows.append({"file": path, "status": "FAIL", "reasons": "; ".join(extra)})

    report = pd.DataFrame(rows)
    report.to_csv(args.out, index=False)
    for row in rows:
        print(f"{row['status']:4s}  {row['file']}" + (f"\n      {row['reasons']}" if row.get("reasons") else ""))
    counts = report["status"].value_counts().to_dict()
    print(f"\n{len(rows)} meshes: " + ", ".join(f"{counts.get(s, 0)} {s}" for s in ("OK", "WARN", "FAIL"))
          + f" -> {args.out}")
    return 1 if counts.get("FAIL", 0) else 0


if __name__ == "__main__":
    sys.exit(main())

# Command line: download the selected Google Scanned Objects and write their manifest.
"""
Usage (from the repository root; needs access to fuel.gazebosim.org):

    python scripts/fetch_gso.py [--selection data/gso/selection.csv] [--out gt/gso] [--count 20]

Takes the ``primary`` objects of the selection in rank order; an object that cannot be found or downloaded is
replaced by the next ``alternate`` and the replacement is recorded. Each object is extracted to
``<out>/<name>/`` (GT mesh: ``meshes/model.obj``), and ``<out>/manifest.csv`` is written with the source, URL,
author and license read from Fuel. Then check the meshes:

    python scripts/check_gt.py --manifest gt/gso/manifest.csv --out gt/gso/gt_report.csv
"""
import argparse
import os
import sys
import urllib.error

import pandas as pd

from ..datasets.gso import API, fetch
from ..datasets.manifest import MANIFEST_COLUMNS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selection", default=os.path.join("data", "gso", "selection.csv"))
    parser.add_argument("--out", default=os.path.join("gt", "gso"))
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    try:
        rows, skipped = fetch(pd.read_csv(args.selection), args.out, args.count)
    except (urllib.error.URLError, OSError) as exc:
        print(f"Cannot reach {API}: {exc}", file=sys.stderr)
        return 2
    for name, reason in skipped:
        print(f"skip  {name}: {reason}")
    manifest = os.path.join(args.out, "manifest.csv")
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(manifest, index=False)
    print(f"\n{len(rows)}/{args.count} objects -> {manifest}")
    return 0 if len(rows) == args.count else 1


if __name__ == "__main__":
    sys.exit(main())

# GT manifest: its columns, the mesh files to check and the problems of each manifest row.
"""One row per GT mesh (template: ``docs/gt/manifest_template.csv``); checked by ``meshcomparison.cli.check_gt``."""
import datetime
import os

import pandas as pd

from ..analysis.gt_check import SUPPORTED_FORMATS

MANIFEST_COLUMNS = ("object_id", "file", "source", "url", "author", "license", "published_date", "category",
                    "selection_reason", "cleanup_notes", "input_azimuth_deg", "input_elevation_deg")
REQUIRED_FIELDS = ("object_id", "file", "source", "license")


def mesh_files(paths):
    files = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, names in os.walk(path):
                files += [os.path.join(root, n) for n in sorted(names) if n.lower().endswith(SUPPORTED_FORMATS)]
        else:
            files.append(path)
    return files


def manifest_issues(manifest_path, cutoff=None):
    """``{absolute file path: [issues]}`` from the manifest, plus issues of rows whose file is missing."""
    table = pd.read_csv(manifest_path, dtype=str).fillna("")
    missing_columns = [c for c in MANIFEST_COLUMNS if c not in table.columns]
    if missing_columns:
        raise ValueError(f"manifest is missing columns: {', '.join(missing_columns)}")
    base = os.path.dirname(os.path.abspath(manifest_path))
    issues = {}
    for _, row in table.iterrows():
        path = os.path.normpath(os.path.join(base, row["file"]))
        found = []
        found += [f"manifest: empty '{field}'" for field in REQUIRED_FIELDS if not row[field].strip()]
        if not os.path.isfile(path):
            found.append("manifest: file not found")
        if cutoff and row["published_date"]:
            try:
                published = datetime.date.fromisoformat(row["published_date"])
                if published < cutoff:
                    found.append(f"published {published} before the training cutoff {cutoff}: may be in training data")
            except ValueError:
                found.append(f"manifest: published_date '{row['published_date']}' is not YYYY-MM-DD")
        elif cutoff:
            found.append("manifest: no published_date to compare with the training cutoff")
        issues[path] = found
    return issues

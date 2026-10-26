"""Qt-free reading of what a finished run wrote to its output folder, for the 3D view and the results tabs."""
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from ..common.io import load_mesh


@dataclass
class RunMeshes:
    gt: object
    rm_aligned: Optional[object] = None
    heatmap: Optional[object] = None
    heatmap_scale: float = 1.0  # the heatmap mesh is saved with the GT bounding-box diagonal normalized to 1
    heatmap_vmax: Optional[float] = None  # colour-scale maximum in GT units (legend)


def _first_value(csv_path, column):
    """First value of ``column`` in ``csv_path``, or ``None`` if the file or the column is missing."""
    if not os.path.isfile(csv_path):
        return None
    table = pd.read_csv(csv_path)
    return float(table[column].iloc[0]) if column in table else None


def load_run_meshes(gt_path, out_dir, with_heatmap):
    """GT, aligned RM and (when the geometric pipeline ran) heatmap mesh with its scale and legend range."""
    metrics = os.path.join(out_dir, "metrics")
    aligned = os.path.join(out_dir, "aligned", "rm_aligned.ply")
    heatmap_path = os.path.join(out_dir, "heatmaps", "gt_heatmap_colored.ply")

    result = RunMeshes(gt=load_mesh(gt_path), rm_aligned=load_mesh(aligned) if os.path.isfile(aligned) else None)
    if with_heatmap and os.path.isfile(heatmap_path):
        result.heatmap = load_mesh(heatmap_path)
        for csv in ("metrics_geometry.csv", "run_metadata.csv"):
            scale = _first_value(os.path.join(metrics, csv), "gt_bbox_diagonal_original_units")
            if scale is not None:
                result.heatmap_scale = scale
                break
        # upper end of the colour scale in GT units, as written by the geometric pipeline
        result.heatmap_vmax = _first_value(os.path.join(metrics, "metrics_geometry.csv"), "heatmap_vmax_gt_units")
    return result


def _text(row, column):
    """String value of ``column`` in ``row``, "" when missing or empty (pandas reads empty cells as NaN)."""
    value = row.get(column, "")
    return "" if pd.isna(value) else str(value).strip()


def geometry_notes(df):
    """
    ``(notes, warnings)`` shown under the geometric table, from the run columns of ``metrics_geometry.csv``.

    ``notes``: sampling, alignment (with the MSE before and after it) and input view. ``warnings``: GT/RM files that
    are scenes with several meshes or ignored geometry; every mesh entered the metrics, which may be unintended.
    """
    row = df.iloc[0].to_dict()
    notes = [f"{int(row['n_samples']):,} area-uniform surface samples per mesh; distances in GT units, scores in "
             "[0, 1]; τ as % of the GT bounding-box diagonal."]
    pre, post = row.get("pre_alignment_mse_normalized"), row.get("post_alignment_mse_normalized")
    mse = f"symmetric MSE {pre:.3g} → {post:.3g} (normalized)" if pre is not None and post is not None else ""
    if bool(row["alignment_triggered"]):
        notes.append(f"Similarity ICP applied (scale {row['icp_scale']:.4f}); {mse}.")
    else:
        threshold = row.get("mse_threshold_normalized")
        notes.append(f"ICP not applied: pre-alignment MSE {pre:.3g} ≤ threshold {threshold:.3g}."
                     if pre is not None and threshold is not None else "ICP not applied.")
    az, el = row.get("input_azimuth_deg"), row.get("input_elevation_deg")
    if az is not None and el is not None and not (pd.isna(az) or pd.isna(el)):
        notes.append(f"Input view: azimuth {az:g}°, elevation {el:g}°. Visible / hidden: GT regions seen from it "
                     "(share of the GT surface in the column header).")
    else:
        notes.append("No input view set: whole surface only. Set one to split the metrics into visible / hidden.")
    warnings = [f"{name} file is a scene; all its meshes entered the metrics: {text}"
                for name, text in (("GT", _text(row, "gt_scene_meshes")), ("RM", _text(row, "rm_scene_meshes")))
                if text]
    return notes, warnings

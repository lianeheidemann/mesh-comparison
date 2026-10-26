import pandas as pd
import trimesh

from meshcomparison.gui.outputs import geometry_notes, load_run_meshes


def _write_run(out):
    (out / "aligned").mkdir(parents=True)
    (out / "heatmaps").mkdir()
    (out / "metrics").mkdir()
    sphere = trimesh.creation.icosphere()
    shifted = sphere.copy()
    shifted.apply_translation([0.05, 0.0, 0.0])
    shifted.export(out / "aligned" / "rm_aligned.ply")
    sphere.export(out / "heatmaps" / "gt_heatmap_colored.ply")
    pd.DataFrame([{"gt_bbox_diagonal_original_units": 3.5, "heatmap_vmax_gt_units": 0.04}]).to_csv(
        out / "metrics" / "metrics_geometry.csv", index=False)
    return sphere, shifted


def test_run_meshes_read_scale_and_legend_range(tmp_path):
    gt = tmp_path / "gt.ply"
    sphere, shifted = _write_run(tmp_path / "out")
    sphere.export(gt)

    meshes = load_run_meshes(str(gt), str(tmp_path / "out"), with_heatmap=True)

    assert meshes.rm_aligned is not None and meshes.heatmap is not None
    assert meshes.heatmap_scale == 3.5
    assert meshes.heatmap_vmax == 0.04  # written by the geometric pipeline


def test_run_meshes_without_geometric_pipeline_has_no_heatmap(tmp_path):
    gt = tmp_path / "gt.ply"
    sphere, _ = _write_run(tmp_path / "out")
    sphere.export(gt)

    meshes = load_run_meshes(str(gt), str(tmp_path / "out"), with_heatmap=False)
    assert meshes.heatmap is None and meshes.heatmap_vmax is None


def _geometry_row(**changes):
    row = {"n_samples": 100000, "alignment_triggered": False, "icp_scale": 1.0, "mse_threshold_normalized": 1e-4,
           "pre_alignment_mse_normalized": 6.66e-5, "post_alignment_mse_normalized": 6.66e-5,
           "input_azimuth_deg": float("nan"), "input_elevation_deg": float("nan"),
           "gt_scene_meshes": float("nan"), "rm_scene_meshes": float("nan")}
    return pd.DataFrame([{**row, **changes}])


def test_geometry_notes_without_alignment_or_input_view():
    notes, warnings = geometry_notes(_geometry_row())
    assert notes[0].startswith("100,000 area-uniform surface samples")
    assert notes[1] == "ICP not applied: pre-alignment MSE 6.66e-05 ≤ threshold 0.0001."
    assert notes[2].startswith("No input view set")
    assert warnings == []


def test_geometry_notes_with_alignment_input_view_and_scene():
    notes, warnings = geometry_notes(_geometry_row(
        alignment_triggered=True, icp_scale=0.98765, pre_alignment_mse_normalized=0.02,
        post_alignment_mse_normalized=5e-5, input_azimuth_deg=-135.0, input_elevation_deg=25.264,
        rm_scene_meshes="object 12 tri 86%, ground 2 tri 14%"))
    assert notes[1] == "Similarity ICP applied (scale 0.9877); symmetric MSE 0.02 → 5e-05 (normalized)."
    assert notes[2].startswith("Input view: azimuth -135°, elevation 25.264°.")
    assert warnings == ["RM file is a scene; all its meshes entered the metrics: object 12 tri 86%, ground 2 tri 14%"]

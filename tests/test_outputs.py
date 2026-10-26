import pandas as pd
import trimesh

from meshcomparison.gui.outputs import load_run_meshes


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

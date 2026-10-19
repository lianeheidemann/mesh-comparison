import pandas as pd
import trimesh

from meshcomparison.gui.outputs import load_run_meshes


def _write_run(out, with_vmax=True):
    (out / "aligned").mkdir(parents=True)
    (out / "heatmaps").mkdir()
    (out / "metrics").mkdir()
    sphere = trimesh.creation.icosphere()
    sphere.export(out / "aligned" / "rm_aligned.ply")
    sphere.export(out / "heatmaps" / "gt_heatmap_colored.ply")
    metrics = out / "metrics"
    pd.DataFrame([{"gt_bbox_diagonal_original_units": 3.5}]).to_csv(metrics / "metrics_geometry.csv", index=False)
    if with_vmax:
        pd.DataFrame([{"heatmap_vmax_gt_units": 0.06}]).to_csv(metrics / "run_metadata_geometry.csv", index=False)


def test_run_meshes_read_scale_and_legend_range(tmp_path):
    gt = tmp_path / "gt.ply"
    trimesh.creation.icosphere().export(gt)
    _write_run(tmp_path / "out")

    meshes = load_run_meshes(str(gt), str(tmp_path / "out"), with_heatmap=True)

    assert meshes.rm_aligned is not None and meshes.heatmap is not None
    assert meshes.heatmap_scale == 3.5 and meshes.heatmap_vmax == 0.06


def test_run_meshes_without_geometric_pipeline_or_old_metadata(tmp_path):
    gt = tmp_path / "gt.ply"
    trimesh.creation.icosphere().export(gt)
    _write_run(tmp_path / "out", with_vmax=False)

    assert load_run_meshes(str(gt), str(tmp_path / "out"), with_heatmap=False).heatmap is None
    assert load_run_meshes(str(gt), str(tmp_path / "out"), with_heatmap=True).heatmap_vmax is None

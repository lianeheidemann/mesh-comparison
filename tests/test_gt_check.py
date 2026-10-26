# Tests of the ground-truth mesh checks and of the manifest validation (meshcomparison.cli.check_gt).

import pandas as pd
import pytest
import trimesh

from meshcomparison.analysis.gt_check import assess, check_file, measure
from meshcomparison.cli import check_gt
from meshcomparison.datasets.manifest import MANIFEST_COLUMNS


@pytest.fixture(scope="module")
def meshes(tmp_path_factory):
    folder = tmp_path_factory.mktemp("gt")
    sphere = trimesh.creation.icosphere(subdivisions=3)
    sphere.export(folder / "clean.stl")
    base = trimesh.creation.box(extents=(3, 3, 0.2))
    base.apply_translation([0, 0, -1.2])
    trimesh.util.concatenate([sphere, base]).export(folder / "on_base.stl")
    inner = trimesh.creation.icosphere(subdivisions=2)
    inner.apply_scale(0.5)
    trimesh.util.concatenate([sphere, inner]).export(folder / "inner_shell.stl")
    half = sphere.copy()
    half.update_faces(half.triangles_center[:, 2] > 0)
    half.remove_unreferenced_vertices()
    half.export(folder / "open.stl")
    (folder / "broken.obj").write_text("not a mesh")
    return folder


def test_clean_closed_object_passes(meshes):
    values = measure(str(meshes / "clean.stl"))
    assert values["watertight"] and values["components"] == 1
    assert values["internal_area_fraction"] == 0.0 and values["boundary_edge_fraction"] == 0.0
    assert assess(values) == ("OK", [])


def test_base_or_scenery_is_flagged(meshes):
    status, reasons = assess(measure(str(meshes / "on_base.stl")))
    assert status == "WARN" and "separate parts" in reasons[0]


def test_hidden_inner_shell_is_flagged(meshes):
    values = measure(str(meshes / "inner_shell.stl"))
    # the inner sphere has a quarter of the outer area: about 20 % of the total surface is enclosed
    assert values["internal_area_fraction"] == pytest.approx(0.2, abs=0.02)
    assert any("enclosed" in r for r in assess(values)[1])


def test_holes_are_flagged(meshes):
    values = measure(str(meshes / "open.stl"))
    assert not values["watertight"] and values["boundary_edge_fraction"] > 0.01
    assert any("open surface" in r for r in assess(values)[1])


def test_unreadable_and_unsupported_files_fail(meshes, tmp_path):
    assert check_file(str(meshes / "broken.obj"))["status"] == "FAIL"
    (tmp_path / "model.fbx").write_text("x")
    assert "unsupported format" in check_file(str(tmp_path / "model.fbx"))["reasons"]


def test_manifest_flags_missing_fields_files_and_training_cutoff(meshes, tmp_path):
    rows = [
        {"object_id": "a", "file": str(meshes / "clean.stl"), "source": "own scan", "license": "CC0",
         "published_date": "2026-09-01"},
        {"object_id": "b", "file": str(meshes / "on_base.stl"), "source": "", "license": "",
         "published_date": "2023-01-01"},
        {"object_id": "c", "file": "missing.stl", "source": "x", "license": "CC-BY-4.0", "published_date": ""},
    ]
    manifest = pd.DataFrame(rows).reindex(columns=MANIFEST_COLUMNS)
    manifest_path = tmp_path / "manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    out = tmp_path / "report.csv"

    assert check_gt.main(["--manifest", str(manifest_path), "--cutoff", "2025-06-01", "--out", str(out)]) == 1
    report = pd.read_csv(out).set_index("file")
    clean = report.loc[str(meshes / "clean.stl")]
    assert clean["status"] == "OK"
    on_base = report.loc[str(meshes / "on_base.stl")]["reasons"]
    assert "empty 'source'" in on_base and "empty 'license'" in on_base and "training cutoff" in on_base
    missing = report.loc[str(tmp_path / "missing.stl")]
    assert missing["status"] == "FAIL" and "file not found" in missing["reasons"]

# Tests of the GSO download (meshcomparison.datasets.gso) against an in-memory stand-in for Gazebo Fuel.
import io
import json
import urllib.error
import zipfile
from pathlib import Path

import pandas as pd
import pytest
import trimesh

from meshcomparison.cli import fetch_gso as fetch_gso_cli
from meshcomparison.datasets import gso as fetch_gso
from meshcomparison.datasets.manifest import MANIFEST_COLUMNS, manifest_issues

ROOT = Path(__file__).resolve().parents[1]


def _gso_zip():
    """Archive laid out like a GSO model: OBJ and MTL in meshes/, texture in materials/textures/."""
    obj = trimesh.exchange.obj.export_obj(trimesh.creation.box(), include_texture=False)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("model.sdf", "<sdf/>")
        archive.writestr("meshes/model.obj", "mtllib model.mtl\n" + obj)
        archive.writestr("meshes/model.mtl", "newmtl material_0\nmap_Kd texture.png\n")
        archive.writestr("materials/textures/texture.png", b"png")
    return buffer.getvalue()


def _fake_fuel(available):
    """``get`` that serves metadata and the archive (latest-version URL only) for the names in ``available``."""
    def get(url, timeout=60):
        for name in available:
            if url == fetch_gso.model_url(name):
                return json.dumps({"name": name, "owner": "GoogleResearch", "license_name": "Test License",
                                   "upload_date": "2022-04-01T00:00:00Z"}).encode()
            if url == fetch_gso.zip_urls(name)[0]:
                return _gso_zip()
        raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
    return get


def _selection():
    return pd.DataFrame([
        {"rank": 1, "gso_name": "A", "role": "primary", "category": "animal", "selection_reason": "r1"},
        {"rank": 2, "gso_name": "Missing", "role": "primary", "category": "figure", "selection_reason": "r2"},
        {"rank": 3, "gso_name": "C", "role": "primary", "category": "vehicle", "selection_reason": "r3"},
        {"rank": 4, "gso_name": "Alt", "role": "alternate", "category": "toy", "selection_reason": "r4"},
        {"rank": 5, "gso_name": "Unused", "role": "alternate", "category": "toy", "selection_reason": "r5"},
    ])


def test_missing_primary_is_replaced_by_the_next_alternate(tmp_path):
    rows, skipped = fetch_gso.fetch(_selection(), str(tmp_path), count=3, get=_fake_fuel({"A", "C", "Alt", "Unused"}))

    assert [r["object_id"] for r in rows] == ["gso_A", "gso_C", "gso_Alt"]
    assert skipped == [("Missing", "not found on Fuel")]
    assert rows[2]["selection_reason"] == "r4 (replaces Missing)"
    assert rows[0]["license"] == "Test License" and rows[0]["published_date"] == "2022-04-01"
    assert rows[0]["file"] == "A/meshes/model.obj"


def test_download_copies_the_texture_next_to_the_mtl(tmp_path):
    mesh = fetch_gso.download("A", str(tmp_path), get=_fake_fuel({"A"}))

    assert Path(mesh) == tmp_path / "A" / "meshes" / "model.obj"
    assert (tmp_path / "A" / "meshes" / "texture.png").read_bytes() == b"png"


def test_manifest_passes_the_manifest_checks(tmp_path):
    rows, _ = fetch_gso.fetch(_selection(), str(tmp_path), count=2, get=_fake_fuel({"A", "C"}))
    manifest = tmp_path / "manifest.csv"
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(manifest, index=False)

    issues = manifest_issues(str(manifest))
    assert len(issues) == 2 and all(found == [] for found in issues.values())


def test_selection_file_lists_20_primaries():
    selection = pd.read_csv(ROOT / "data" / "gso" / "selection.csv")
    assert (selection["role"] == "primary").sum() == 20
    assert selection["gso_name"].is_unique and selection["rank"].is_unique


def test_unreachable_fuel_stops_instead_of_skipping_everything(tmp_path, monkeypatch):
    def offline(url, timeout=60):
        raise urllib.error.URLError("tunnel refused")
    monkeypatch.setattr(fetch_gso, "_get", offline)
    selection = tmp_path / "selection.csv"
    _selection().to_csv(selection, index=False)

    with pytest.raises(urllib.error.URLError):  # not reported as missing objects
        fetch_gso.fetch(_selection(), str(tmp_path), count=2)
    assert fetch_gso_cli.main(["--selection", str(selection), "--out", str(tmp_path / "gso"), "--count", "2"]) == 2

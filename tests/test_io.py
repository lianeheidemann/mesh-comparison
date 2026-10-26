# Loading of multi-object glTF scenes: only triangle meshes enter; cameras, lights and lines are left out and reported.
import base64
import json

import numpy as np
import pytest
import trimesh

from meshcomparison.analysis.gt_check import check_file
from meshcomparison.common.io import describe_scene, load_mesh


def _write_scene(path):
    """glTF with an object (box), a ground plane, a line helper, a camera and a light (KHR_lights_punctual)."""
    box = trimesh.creation.box()
    ground = trimesh.Trimesh([[-3, -3, -0.5], [3, -3, -0.5], [3, 3, -0.5], [-3, 3, -0.5]], [[0, 1, 2], [0, 2, 3]])
    blobs, views, accessors = [], [], []

    def add(array, target, component, kind):
        offset = sum(len(b) for b in blobs)
        data = array.tobytes()
        blobs.append(data + b"\0" * (-len(data) % 4))
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target})
        accessor = {"bufferView": len(views) - 1, "componentType": component, "count": int(len(array)), "type": kind}
        if kind == "VEC3":
            accessor.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        accessors.append(accessor)
        return len(accessors) - 1

    meshes = []
    for mesh in (box, ground):
        position = add(np.asarray(mesh.vertices, np.float32), 34962, 5126, "VEC3")
        indices = add(np.asarray(mesh.faces, np.uint32).ravel(), 34963, 5125, "SCALAR")
        meshes.append({"primitives": [{"attributes": {"POSITION": position}, "indices": indices, "mode": 4}]})
    line = add(np.array([[0, 0, 0], [0, 0, 3]], np.float32), 34962, 5126, "VEC3")
    meshes.append({"primitives": [{"attributes": {"POSITION": line}, "mode": 1}]})
    buffer = b"".join(blobs)
    gltf = {
        "asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0, 1, 2, 3, 4]}],
        "nodes": [{"mesh": 0, "name": "object"}, {"mesh": 1, "name": "ground"}, {"mesh": 2, "name": "gizmo"},
                  {"camera": 0, "name": "camera", "translation": [0, -5, 2]},
                  {"name": "sun", "extensions": {"KHR_lights_punctual": {"light": 0}}}],
        "meshes": meshes, "cameras": [{"type": "perspective", "perspective": {"yfov": 0.8, "znear": 0.1}}],
        "extensionsUsed": ["KHR_lights_punctual"],
        "extensions": {"KHR_lights_punctual": {"lights": [{"type": "directional"}]}},
        "accessors": accessors, "bufferViews": views,
        "buffers": [{"byteLength": len(buffer),
                     "uri": "data:application/octet-stream;base64," + base64.b64encode(buffer).decode()}],
    }
    path.write_text(json.dumps(gltf))
    return box, ground


@pytest.fixture
def scene(tmp_path):
    path = tmp_path / "scene.gltf"
    box, ground = _write_scene(path)
    return path, box, ground


def test_only_triangle_meshes_enter_and_the_scene_is_reported(scene, capsys):
    path, box, ground = scene
    mesh = load_mesh(str(path))
    assert len(mesh.faces) == len(box.faces) + len(ground.faces)  # the line, camera and light add nothing
    printed = capsys.readouterr().out
    assert "ground" in printed and "gizmo (Path3D)" in printed


def test_describe_scene_lists_meshes_by_area_and_dropped_items(scene):
    path, box, ground = scene
    description = describe_scene(str(path))
    names = [m["node"] for m in description["meshes"]]
    assert names == ["ground", "object"]  # the 6 x 6 ground plane has more area than the unit box
    fractions = {m["node"]: m["area_fraction"] for m in description["meshes"]}
    assert fractions["object"] == pytest.approx(box.area / (box.area + ground.area))
    assert description["dropped"] == [{"node": "gizmo", "type": "Path3D"}]


def test_check_gt_names_the_extra_scene_mesh(scene):
    row = check_file(str(scene[0]))
    assert row["status"] == "WARN"
    assert "scene meshes: ground: 2 tri, 86%; object: 12 tri, 14%" in row["reasons"]
    assert row["dropped"] == "gizmo (Path3D)"


def test_single_mesh_files_load_unchanged(tmp_path, capsys):
    sphere = trimesh.creation.icosphere(subdivisions=2)
    sphere.export(tmp_path / "sphere.stl")
    mesh = load_mesh(str(tmp_path / "sphere.stl"))
    assert len(mesh.faces) == len(sphere.faces)
    assert capsys.readouterr().out == ""  # nothing to report for a single mesh

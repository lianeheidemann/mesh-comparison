import os

import trimesh


def ensure_dirs(base_out, subdirs):
    """Create ``base_out/<relative path>`` for each entry of ``subdirs`` ({key: relative path parts})."""
    paths = {key: os.path.join(base_out, *parts) for key, parts in subdirs.items()}
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def _instances(path):
    """``(kept, dropped)`` instances of the file's scene graph, transforms baked in. ``kept`` holds
    ``(node name, Trimesh)`` for triangle meshes; ``dropped`` holds ``(node name, type name)`` for other geometry
    (lines, points). Cameras and lights are not geometry and never appear; skins and animations are not applied
    (meshes come in their rest pose)."""
    loaded = trimesh.load(path, force='scene', process=False, maintain_order=True)
    if isinstance(loaded, trimesh.Trimesh):
        return [(os.path.basename(path), loaded.copy())], []
    if not isinstance(loaded, trimesh.Scene):
        raise TypeError(f"Unsupported loaded type for {path}: {type(loaded)}")

    kept, dropped = [], []
    for node_name in loaded.graph.nodes_geometry:
        try:
            transform, geom_name = loaded.graph[node_name]
        except Exception:
            continue
        geom = loaded.geometry.get(geom_name)
        if isinstance(geom, trimesh.Trimesh) and len(geom.faces):
            g = geom.copy()
            g.apply_transform(transform)
            kept.append((node_name, g))
        elif geom is not None:
            dropped.append((node_name, type(geom).__name__))
    if not kept:
        # no instanced triangle mesh in the graph: use the geometries without transforms
        kept = [(name, g.copy()) for name, g in loaded.geometry.items()
                if isinstance(g, trimesh.Trimesh) and len(g.faces)]
        dropped = [(name, type(g).__name__) for name, g in loaded.geometry.items()
                   if not (isinstance(g, trimesh.Trimesh) and len(g.faces))]
    return kept, dropped


def _describe(kept, dropped):
    areas = [float(m.area) for _, m in kept]
    total = sum(areas) or 1.0
    meshes = [{"node": name, "triangles": int(len(m.faces)), "area_fraction": area / total}
              for (name, m), area in zip(kept, areas)]
    meshes.sort(key=lambda row: -row["area_fraction"])
    return {"meshes": meshes, "dropped": [{"node": name, "type": kind} for name, kind in dropped]}


def describe_scene(path):
    """What ``load_mesh`` takes from ``path``: ``{"meshes": [{"node", "triangles", "area_fraction"}, ...],
    "dropped": [{"node", "type"}, ...]}``, meshes sorted by area (largest first)."""
    return _describe(*_instances(path))


def scene_summary(description):
    """One line such as ``object 12 tri 86 %, ground 2 tri 14 %; ignored: gizmo (Path3D)``."""
    text = ", ".join(f"{m['node']} {m['triangles']} tri {m['area_fraction']:.0%}" for m in description["meshes"])
    if description["dropped"]:
        text += "; ignored: " + ", ".join(f"{d['node']} ({d['type']})" for d in description["dropped"])
    return text


def load_mesh(path):
    """
    Triangle mesh of a file (STL/OBJ/PLY/OFF/GLB/GLTF via trimesh): every triangle mesh of the scene, with its
    scene transform, concatenated. Lines and points are dropped; cameras, lights, skins and animations are not
    geometry and do not enter. When a scene has several meshes or dropped items, a one-line summary is printed so
    extra objects (ground, scenery) are visible. This does NOT support FBX.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".fbx":
        raise ValueError(
            f"FBX is not supported in this pipeline: {path}\n"
            f"Please convert it first (e.g. in Blender) to GLB, which keeps textures, or to OBJ/PLY."
        )

    try:
        kept, dropped = _instances(path)
        if not kept:
            raise ValueError(f"No triangle geometry found in: {path}")
        if len(kept) > 1 or dropped:
            print(f"    Scene {os.path.basename(path)}: {scene_summary(_describe(kept, dropped))}")
        meshes = [m for _, m in kept]
        mesh = meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)
        mesh.remove_unreferenced_vertices()
        return mesh

    except Exception as e:
        raise RuntimeError(f"Could not load mesh file: {path}\nReason: {e}")

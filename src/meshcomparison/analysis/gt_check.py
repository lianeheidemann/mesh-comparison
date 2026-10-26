# Checks whether a mesh is usable as a ground truth (single object, clean surface, no hidden faces) and reports why not.
"""
Ground-truth (GT) mesh checks.

Each check returns a measured value; ``assess`` turns the values into ``OK`` / ``WARN`` / ``FAIL`` with reasons.
The thresholds below are review triggers, not hard rules: a WARN means "look at this mesh before using it".
"""
import os

import numpy as np
import trimesh

from ..common.io import load_mesh
from ..common.sampling import sample_surface

SUPPORTED_FORMATS = (".stl", ".obj", ".ply", ".off", ".glb", ".gltf")

MAX_SECONDARY_AREA = 0.05  # share of the area outside the largest connected part (base, scenery, loose parts)
MAX_BOUNDARY_EDGES = 0.01  # share of edges used by one face only (holes, open surface)
MAX_INTERNAL_AREA = 0.02  # share of the surface enclosed by the mesh itself (hidden faces, inner shells)
MAX_DEGENERATE_FACES = 0.01  # share of zero-area faces

N_INTERNAL_SAMPLES = 20_000
RAY_DIRECTIONS = np.array(
    [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]
    + [[x, y, z] for x in (1, -1) for y in (1, -1) for z in (1, -1)], dtype=np.float64)
RAY_DIRECTIONS /= np.linalg.norm(RAY_DIRECTIONS, axis=1, keepdims=True)


def _has_texture(mesh):
    visual = mesh.visual
    if visual.kind == "texture":
        material = getattr(visual, "material", None)
        image = getattr(material, "image", None) or getattr(material, "baseColorTexture", None)
        return image is not None
    if visual.kind == "vertex":
        colors = np.asarray(visual.vertex_colors)
        return len(colors) > 0 and len(np.unique(colors, axis=0)) > 1
    return False


def edge_statistics(mesh):
    """Shares of boundary edges (used by one face) and counts of non-manifold edges (used by more than two)."""
    _, counts = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
    return {
        "boundary_edge_fraction": float(np.mean(counts == 1)) if len(counts) else 0.0,
        "nonmanifold_edges": int(np.sum(counts > 2)),
    }


def component_statistics(mesh):
    """Number of face-connected parts and the share of the area outside the largest one."""
    labels = trimesh.graph.connected_component_labels(mesh.face_adjacency, node_count=len(mesh.faces))
    area_per_part = np.bincount(labels, weights=mesh.area_faces)
    return {
        "components": int(len(area_per_part)),
        "secondary_area_fraction": float(1.0 - area_per_part.max() / area_per_part.sum()),
    }


def internal_area_fraction(mesh, n_samples=N_INTERNAL_SAMPLES, seed=0):
    """Share of the surface from which every one of 14 rays (axes and diagonals) hits the mesh again: faces hidden
    inside the object (inner shells, overlapping parts, eyes inside a head). Deep concavities can also count."""
    import open3d as o3d

    diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
    points, normals = sample_surface(mesh, n_samples, seed, return_normals=True)
    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(o3d.core.Tensor(np.asarray(mesh.vertices, dtype=np.float32)),
                        o3d.core.Tensor(np.asarray(mesh.faces, dtype=np.uint32)))
    enclosed = np.ones(len(points), dtype=bool)
    for direction in RAY_DIRECTIONS:
        # start just off the surface on the side the ray leaves, so a ray does not hit its own face
        side = np.sign(normals @ direction)[:, None]
        side[side == 0] = 1.0
        origins = points + 1e-4 * diag * side * normals
        rays = np.hstack([origins, np.broadcast_to(direction, origins.shape)]).astype(np.float32)
        hits = scene.cast_rays(o3d.core.Tensor(rays))["t_hit"].numpy()
        enclosed &= np.isfinite(hits)
    return float(np.mean(enclosed))


def measure(path):
    """All measurements of the mesh at ``path`` (raises if it cannot be loaded)."""
    mesh = load_mesh(path)
    merged = mesh.copy()
    merged.merge_vertices()
    extents = merged.bounds[1] - merged.bounds[0]
    areas = merged.area_faces
    diag = float(np.linalg.norm(extents))
    values = {
        "vertices": int(len(merged.vertices)),
        "faces": int(len(merged.faces)),
        "surface_area": float(areas.sum()),
        "bbox_diagonal": diag,
        "extent_x": float(extents[0]), "extent_y": float(extents[1]), "extent_z": float(extents[2]),
        "degenerate_face_fraction": float(np.mean(areas <= 1e-12 * diag ** 2)) if len(areas) else 1.0,
        "duplicate_faces": int(len(merged.faces) - len(np.unique(np.sort(merged.faces, axis=1), axis=0))),
        "watertight": bool(merged.is_watertight),
        "has_texture": _has_texture(mesh),
    }
    if len(merged.faces) and values["surface_area"] > 0:
        values.update(edge_statistics(merged))
        values.update(component_statistics(merged))
        values["internal_area_fraction"] = internal_area_fraction(merged)
    return values


def assess(values):
    """``(status, reasons)`` from the measurements: FAIL if the mesh cannot be evaluated, WARN if it needs a look."""
    if values.get("faces", 0) == 0 or values.get("surface_area", 0.0) <= 0:
        return "FAIL", ["no triangles or zero surface area"]
    reasons = []
    if values["secondary_area_fraction"] > MAX_SECONDARY_AREA:
        reasons.append(f"{values['components']} separate parts; {values['secondary_area_fraction']:.0%} of the area "
                       "is outside the largest (base, scenery or loose parts?)")
    if values["boundary_edge_fraction"] > MAX_BOUNDARY_EDGES:
        reasons.append(f"open surface: {values['boundary_edge_fraction']:.1%} boundary edges (holes?)")
    if values["internal_area_fraction"] > MAX_INTERNAL_AREA:
        reasons.append(f"{values['internal_area_fraction']:.1%} of the surface is enclosed by the mesh "
                       "(hidden or overlapping faces?)")
    if values["nonmanifold_edges"] > 0:
        reasons.append(f"{values['nonmanifold_edges']} non-manifold edges")
    if values["degenerate_face_fraction"] > MAX_DEGENERATE_FACES:
        reasons.append(f"{values['degenerate_face_fraction']:.1%} zero-area faces")
    if values["duplicate_faces"] > 0:
        reasons.append(f"{values['duplicate_faces']} duplicate faces")
    return ("WARN" if reasons else "OK"), reasons


def check_file(path):
    """One report row for ``path``: status, reasons and measurements (FAIL with the error if it cannot be read)."""
    row = {"file": path}
    if os.path.splitext(path)[1].lower() not in SUPPORTED_FORMATS:
        return {**row, "status": "FAIL", "reasons": f"unsupported format (use {', '.join(SUPPORTED_FORMATS)})"}
    try:
        values = measure(path)
    except Exception as exc:  # unreadable file: report it, keep checking the others
        return {**row, "status": "FAIL", "reasons": f"cannot load: {str(exc).splitlines()[-1].strip()}"}
    status, reasons = assess(values)
    return {**row, "status": status, "reasons": "; ".join(reasons), **values}

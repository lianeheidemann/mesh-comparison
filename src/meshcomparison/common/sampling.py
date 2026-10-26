"""Area-uniform surface sampling shared by alignment, metrics and visibility (fixed seeds, reproducible)."""
import numpy as np

N_SAMPLES = 100_000
SEED_GT = 0
SEED_RM = 1


def sample_surface(mesh, n, seed, return_normals=False):
    """``n`` points drawn uniformly over the surface of ``mesh`` (faces chosen by area, uniform barycentrics).

    With ``return_normals`` also returns the unit normal of the face of each point (the random draws, and so the
    points, are the same either way)."""
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces)
    if len(faces) == 0:
        raise ValueError("Mesh has no faces; surface sampling needs a triangle mesh.")
    tri = vertices[faces]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    total = areas.sum()
    if not np.isfinite(total) or total <= 0:
        raise ValueError("Mesh has zero surface area; surface sampling is not possible.")

    rng = np.random.default_rng(seed)
    face_idx = rng.choice(len(faces), size=n, p=areas / total)
    r1 = np.sqrt(rng.random(n))
    r2 = rng.random(n)
    a, b, c = tri[face_idx, 0], tri[face_idx, 1], tri[face_idx, 2]
    points = (1.0 - r1)[:, None] * a + (r1 * (1.0 - r2))[:, None] * b + (r1 * r2)[:, None] * c
    if not return_normals:
        return points
    normals = cross[face_idx] / (2.0 * areas[face_idx])[:, None]  # only faces with area > 0 are ever drawn
    return points, normals

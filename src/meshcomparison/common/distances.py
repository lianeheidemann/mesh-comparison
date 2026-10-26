import numpy as np
from scipy.spatial import cKDTree


def maybe_subsample(points, max_points=50000, seed=0):
    if len(points) <= max_points:
        return points
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(points), size=max_points, replace=False)
    return points[idx]


def nn_distances(src_points, dst_points):
    tree = cKDTree(dst_points)
    dists, idx = tree.query(src_points, k=1, workers=-1)
    return dists, idx


def surface_distances(points, mesh):
    """Distance from each point to the closest point on the triangles of ``mesh`` (exact, not to its vertices or
    samples) and the unit normal of that triangle. Uses Open3D's Embree scene; coordinates go through float32, so
    distances carry an absolute error of about 1e-7 for unit-scale meshes."""
    import open3d as o3d

    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(o3d.core.Tensor(np.asarray(mesh.vertices, dtype=np.float32)),
                        o3d.core.Tensor(np.asarray(mesh.faces, dtype=np.uint32)))
    points = np.asarray(points, dtype=np.float64)
    result = scene.compute_closest_points(o3d.core.Tensor(points.astype(np.float32)))
    closest = result["points"].numpy().astype(np.float64)
    normals = result["primitive_normals"].numpy().astype(np.float64)
    return np.linalg.norm(points - closest, axis=1), normals


def symmetric_surface_mse(gt_points, rm_points, gt_mesh, rm_mesh):
    """Mean of the two directional mean squared point-to-surface distances (GT samples to the RM surface and back)."""
    d_gt2rm, _ = surface_distances(gt_points, rm_mesh)
    d_rm2gt, _ = surface_distances(rm_points, gt_mesh)
    return 0.5 * (np.mean(d_gt2rm ** 2) + np.mean(d_rm2gt ** 2))

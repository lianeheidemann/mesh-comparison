import numpy as np
import pytest
import trimesh

from meshcomparison.common.alignment import axis_rotations, initial_similarity, principal_axis_rotations
from meshcomparison.common.distances import maybe_subsample, surface_distances, symmetric_surface_mse
from meshcomparison.common.sampling import sample_surface
from meshcomparison.common.transforms import apply_transform_points


@pytest.fixture
def cloud():
    rng = np.random.default_rng(0)
    return rng.random((200, 3))


def _unit_triangle():
    return trimesh.Trimesh([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], [[0, 1, 2]], process=False)


def test_surface_distance_to_face_edge_and_vertex():
    points = np.array([[0.2, 0.2, 0.5],    # above the face: closest point inside the triangle
                       [0.5, -0.3, 0.4],   # beside the edge y = 0: closest point on that edge
                       [-0.3, -0.4, 0.0]])  # beyond vertex (0, 0, 0)
    distances, normals = surface_distances(points, _unit_triangle())
    assert np.allclose(distances, [0.5, 0.5, 0.5], atol=1e-6)
    assert np.allclose(np.abs(normals[:, 2]), 1.0)


def test_symmetric_surface_mse_is_zero_for_the_same_surface_and_delta_squared_for_a_shift():
    box = trimesh.creation.box()
    a, b = sample_surface(box, 5000, 0), sample_surface(box, 5000, 1)
    assert symmetric_surface_mse(a, b, box, box) < 1e-12  # independent samples, same surface

    square = trimesh.Trimesh([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [[0, 1, 2], [0, 2, 3]], process=False)
    shifted = square.copy()
    shifted.apply_translation([0.0, 0.0, 0.03])
    pa, pb = sample_surface(square, 2000, 0), sample_surface(shifted, 2000, 1)
    assert symmetric_surface_mse(pa, pb, square, shifted) == pytest.approx(0.03 ** 2, rel=1e-4)


def test_maybe_subsample_limits_size(cloud):
    assert len(maybe_subsample(cloud, max_points=50)) == 50
    assert maybe_subsample(cloud, max_points=1000) is cloud


def test_axis_rotations_are_the_24_distinct_proper_rotations():
    rotations = axis_rotations()
    assert len(rotations) == 24
    assert all(np.allclose(r @ r.T, np.eye(3)) and np.isclose(np.linalg.det(r), 1.0) for r in rotations)
    assert len({tuple(r.ravel()) for r in rotations}) == 24


def test_initial_similarity_undoes_a_known_rotation_scale_and_shift(cloud):
    rotation = trimesh.transformations.rotation_matrix(1.0, [1, 2, 3])[:3, :3]
    moved = 2.0 * cloud @ rotation.T + np.array([1.0, -2.0, 3.0])
    T = initial_similarity(moved, cloud, rotation.T)
    assert np.allclose(apply_transform_points(moved, T), cloud, atol=1e-9)


def test_principal_axes_give_the_rotation_of_an_anisotropic_cloud():
    points = np.random.default_rng(0).normal(size=(2000, 3)) * np.array([3.0, 2.0, 1.0])
    rotation = trimesh.transformations.rotation_matrix(2.0, [1, -1, 0.5])[:3, :3]
    moved = points @ rotation.T
    errors = [np.linalg.norm(r - rotation.T) for r in principal_axis_rotations(moved, points)]
    assert min(errors) < 1e-6

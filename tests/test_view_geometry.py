# Tests of the 3D viewer's camera, bounds and floor geometry (gui/view_geometry.py) with hand-computed values.
import numpy as np
import pytest

from meshcomparison.gui.view_geometry import (
    combined_bounds, constrained_camera_position, floor_plane, placeholder_camera_bounds, view_direction,
)


def test_view_direction_matches_the_evaluation_camera():
    # az -135 deg points to (-1, -1) in the xy plane; elevation 25.264 deg ~ atan(1/sqrt(2)) gives the cube diagonal
    direction = np.array(view_direction(-135.0, np.degrees(np.arctan(1 / np.sqrt(2)))))
    np.testing.assert_allclose(direction, -np.ones(3) / np.sqrt(3) * [1, 1, -1], atol=1e-12)
    assert np.linalg.norm(view_direction(10.0, 70.0)) == pytest.approx(1.0)


@pytest.mark.parametrize("elevation, expected", [(-30.0, 8.0), (45.0, 45.0), (89.0, 78.0)])
def test_elevation_is_clipped_with_azimuth_and_distance_kept(elevation, expected):
    focal = np.array([1.0, 2.0, 3.0])
    position = focal + 5.0 * np.array(view_direction(60.0, elevation))

    moved = np.array(constrained_camera_position(position, focal))

    np.testing.assert_allclose(moved, focal + 5.0 * np.array(view_direction(60.0, expected)), atol=1e-12)


def test_camera_on_the_focal_point_is_left_alone():
    assert constrained_camera_position((1.0, 1.0, 1.0), (1.0, 1.0, 1.0)) is None


def test_combined_bounds_encloses_every_mesh():
    assert combined_bounds([]) is None
    assert combined_bounds([(0, 1, 0, 1, 0, 1), (-2, 0.5, 0.2, 3, 0.5, 4)]) == (-2, 1, 0, 3, 0, 4)


def test_floor_lies_just_below_the_scene():
    center, size, resolution = floor_plane((0.0, 2.0, 0.0, 1.0, 0.0, 2.0))  # diagonal 3
    assert center == pytest.approx((1.0, 0.5, -0.03))  # 1 % of the diagonal below zmin
    assert size == pytest.approx(12.0)  # 4 diagonals
    assert resolution == 25  # int(12 / (0.16 * 3))


def test_floor_has_a_minimum_size_for_tiny_scenes():
    _, size, resolution = floor_plane((0.0, 0.1, 0.0, 0.1, 0.0, 0.1))
    assert size == 3.0 and resolution == 80


def test_placeholder_framing_widens_the_reference_cube():
    side = 0.36
    bounds = placeholder_camera_bounds((-side / 2, side / 2, -side / 2, side / 2, 0.0, side))
    assert bounds == pytest.approx((-0.75, 0.75, -0.75, 0.75, 0.0, side))  # diagonal 0.62 < 0.75 minimum

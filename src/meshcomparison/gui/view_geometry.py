# Camera, bounds and floor geometry of the 3D viewer (z up), as plain numpy so it can be tested without a window.
"""Bounds are ``(xmin, xmax, ymin, ymax, zmin, zmax)`` tuples, as used by PyVista."""
import numpy as np

MIN_ELEVATION_DEG = 8.0  # the camera stays above the floor ...
MAX_ELEVATION_DEG = 78.0  # ... and never looks straight down (no roll-over)


def view_direction(azimuth_deg, elevation_deg):
    """Unit vector from the focal point to the camera; azimuth from +x towards +y, elevation above the xy plane."""
    az, el = np.deg2rad(azimuth_deg), np.deg2rad(elevation_deg)
    return (np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el))


def constrained_camera_position(position, focal_point, min_deg=MIN_ELEVATION_DEG, max_deg=MAX_ELEVATION_DEG):
    """Camera position with the same azimuth and distance but the elevation clipped to ``[min_deg, max_deg]``;
    ``None`` when the camera sits on the focal point."""
    position = np.asarray(position, dtype=float)
    focal_point = np.asarray(focal_point, dtype=float)
    offset = position - focal_point
    distance = float(np.linalg.norm(offset))
    if distance <= 1e-9:
        return None

    direction = offset / distance
    azimuth = float(np.arctan2(direction[1], direction[0]))
    elevation = float(np.arcsin(np.clip(direction[2], -1.0, 1.0)))
    elevation = float(np.clip(elevation, np.deg2rad(min_deg), np.deg2rad(max_deg)))
    horizontal = np.cos(elevation)
    return (
        focal_point[0] + distance * horizontal * np.cos(azimuth),
        focal_point[1] + distance * horizontal * np.sin(azimuth),
        focal_point[2] + distance * np.sin(elevation),
    )


def combined_bounds(bounds_list):
    """Bounds enclosing every entry of ``bounds_list``; ``None`` when it is empty."""
    if not bounds_list:
        return None
    bounds = np.asarray(bounds_list, dtype=float)
    return (
        float(bounds[:, 0].min()), float(bounds[:, 1].max()),
        float(bounds[:, 2].min()), float(bounds[:, 3].max()),
        float(bounds[:, 4].min()), float(bounds[:, 5].max()),
    )


def _diagonal(bounds):
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    return float(np.linalg.norm((xmax - xmin, ymax - ymin, zmax - zmin)))


def floor_plane(bounds):
    """``(center, size, resolution)`` of the square grid drawn just below ``bounds``."""
    xmin, xmax, ymin, ymax, zmin, _ = bounds
    diagonal = max(_diagonal(bounds), 1e-3)
    size = max(diagonal * 4.0, 3.0)
    resolution = max(24, min(80, int(size / max(diagonal * 0.16, 1e-3))))
    center = ((xmin + xmax) / 2, (ymin + ymax) / 2, zmin - diagonal * 0.01)
    return center, size, resolution


def placeholder_camera_bounds(bounds):
    """Wider horizontal framing for the small reference cube shown before any mesh is loaded."""
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    half_extent = max(_diagonal(bounds), 0.75)
    center_x, center_y = (xmin + xmax) / 2, (ymin + ymax) / 2
    return (
        center_x - half_extent, center_x + half_extent,
        center_y - half_extent, center_y + half_extent,
        zmin, zmax,
    )

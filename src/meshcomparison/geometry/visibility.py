# Visible/hidden classification of GT surface samples from the input-image view (z-buffer test).
import numpy as np

from ..common.rendering import render_ortho_depth
from ..common.transforms import apply_transform_points
from ..perceptual.cameras import build_tight_ortho_camera, camera_pose_for_view

DEPTH_RESOLUTION = 1024  # square depth image used for the z-buffer test
DEPTH_TOLERANCE = 0.005  # fraction of the GT diagonal: a sample this close behind the z-buffer counts as visible


def input_view_camera(gt, azimuth_deg, elevation_deg):
    """Orthographic camera of the input view around the GT, with the axis convention of the perceptual views
    (z up, azimuth from +x towards +y)."""
    low, high = gt.bounds
    center, diag = 0.5 * (low + high), float(np.linalg.norm(high - low))
    pose = camera_pose_for_view(center, diag, azimuth_deg, elevation_deg)
    return build_tight_ortho_camera([gt], camera_pose=pose, margin=1.05)


def visible_from_depth(points, camera_cfg, depth, tolerance=DEPTH_TOLERANCE):
    """True for points whose depth along the view axis is within ``tolerance`` of the z-buffer at their pixel."""
    height, width = depth.shape
    cam = apply_transform_points(points, np.linalg.inv(camera_cfg["pose"]))
    u = np.floor((cam[:, 0] / camera_cfg["xmag"] + 1.0) * 0.5 * width).astype(int)
    v = np.floor((1.0 - cam[:, 1] / camera_cfg["ymag"]) * 0.5 * height).astype(int)
    inside = (u >= 0) & (u < width) & (v >= 0) & (v < height)

    visible = np.zeros(len(points), dtype=bool)
    z_buffer = depth[v[inside], u[inside]]
    hit = z_buffer > 0
    visible[np.flatnonzero(inside)[hit]] = -cam[inside, 2][hit] <= z_buffer[hit] + tolerance
    return visible


def gt_visibility(gt, gt_points, azimuth_deg, elevation_deg, resolution=DEPTH_RESOLUTION, tolerance=DEPTH_TOLERANCE):
    """Visibility of ``gt_points`` (samples of ``gt``) from the input view."""
    camera_cfg = input_view_camera(gt, azimuth_deg, elevation_deg)
    depth = render_ortho_depth(gt, camera_cfg, width=resolution, height=resolution)
    return visible_from_depth(gt_points, camera_cfg, depth, tolerance)

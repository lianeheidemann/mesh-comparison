"""Interactive 3D view (PyVista embedded in Qt) of the GT, the aligned RM and the deviation heatmap."""
import numpy as np
import pyvista as pv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget,
)
from pyvistaqt import QtInteractor


GT_COLOR = "#b8bec6"
RM_COLOR = "#e0793b"
VIEW_BACKGROUND = "#10171c"
GRID_COLOR = "#1d2b35"
PLACEHOLDER_COLOR = "#477ca4"
PLACEHOLDER_EDGE = "#80b9e7"
DEFAULT_AZIMUTH = -135.0
DEFAULT_ELEVATION = 25.264


def to_polydata(mesh):
    """Convert a trimesh mesh to PyVista, keeping per-vertex colours when the mesh has them."""
    faces = np.asarray(mesh.faces, dtype=np.int64)
    cells = np.hstack([np.full((len(faces), 1), 3, dtype=np.int64), faces]).ravel()
    poly = pv.PolyData(np.asarray(mesh.vertices, dtype=np.float64), cells)
    visual = getattr(mesh, "visual", None)
    if visual is not None and getattr(visual, "kind", None) == "vertex":
        poly.point_data["rgb"] = np.asarray(visual.vertex_colors)[:, :3].astype(np.uint8)
    return poly


class MeshViewer(QWidget):
    LAYERS = (
        ("gt", "GT"),
        ("rm", "RM aligned"),
        ("heatmap", "Deviation heatmap"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._actors = {}
        self._polys = {}
        self._floor_actor = None
        self._placeholder_actor = None
        self._placeholder_poly = None

        self.plotter = QtInteractor(self)
        self.plotter.set_background(VIEW_BACKGROUND)
        self.plotter.add_axes()
        self.plotter.iren.enable_terrain_style()
        self._camera_observer = self.plotter.iren.add_observer(
            "InteractionEvent", self._constrain_camera_elevation)

        self._checks = {}
        toolbar = QFrame()
        toolbar.setObjectName("viewerToolbar")
        controls = QHBoxLayout(toolbar)
        controls.setContentsMargins(10, 8, 10, 8)
        controls.setSpacing(10)
        for key, label in self.LAYERS:
            box = QCheckBox(label)
            box.setEnabled(False)
            box.toggled.connect(lambda checked, k=key: self._set_visible(k, checked))
            self._checks[key] = box
            controls.addWidget(box)

        controls.addSpacing(12)
        controls.addWidget(QLabel("RM opacity"))
        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(10, 100)
        self.opacity.setValue(100)
        self.opacity.setFixedWidth(110)
        self.opacity.valueChanged.connect(self._on_opacity)
        controls.addWidget(self.opacity)

        self.edges = QCheckBox("Edges")
        self.edges.toggled.connect(self._on_edges)
        controls.addWidget(self.edges)

        reset = QPushButton("Reset view")
        reset.clicked.connect(self.reset_view)
        controls.addWidget(reset)
        shot = QPushButton("Save image…")
        shot.clicked.connect(self._save_screenshot)
        controls.addWidget(shot)
        controls.addStretch(1)

        self.status = QLabel("Select the GT and RM files to preview them here.")
        self.status.setObjectName("hint")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 8)
        layout.setSpacing(8)
        layout.addWidget(toolbar)
        layout.addWidget(self.plotter.interactor, 1)
        layout.addWidget(self.status)
        self._show_placeholder()

    def reset_view(self):
        """Frame the meshes from the same direction as the evaluation renders (z-up, az -135°, el 25.264°)."""
        az, el = np.deg2rad(DEFAULT_AZIMUTH), np.deg2rad(DEFAULT_ELEVATION)
        direction = (np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el))
        self.plotter.view_vector(direction, viewup=(0.0, 0.0, 1.0))
        bounds = self._camera_bounds()
        if bounds is not None:
            self.plotter.reset_camera(bounds=bounds)

    def _constrain_camera_elevation(self, _interactor, _event):
        """Keep the camera above the ground plane and prevent it from rolling over."""
        camera = self.plotter.camera
        position = np.asarray(camera.position, dtype=float)
        focal_point = np.asarray(camera.focal_point, dtype=float)
        offset = position - focal_point
        distance = float(np.linalg.norm(offset))
        if distance <= 1e-9:
            return

        direction = offset / distance
        azimuth = float(np.arctan2(direction[1], direction[0]))
        elevation = float(np.arcsin(np.clip(direction[2], -1.0, 1.0)))
        elevation = float(np.clip(elevation, np.deg2rad(8), np.deg2rad(78)))
        horizontal = np.cos(elevation)
        camera.position = (
            focal_point[0] + distance * horizontal * np.cos(azimuth),
            focal_point[1] + distance * horizontal * np.sin(azimuth),
            focal_point[2] + distance * np.sin(elevation),
        )
        camera.up = (0.0, 0.0, 1.0)
        camera.OrthogonalizeViewUp()

    def close_plotter(self):
        self.plotter.close()

    def _show_placeholder(self):
        """Show a simple reference cube while no input meshes are loaded."""
        if self._actors or self._placeholder_actor is not None:
            return
        side = 0.36
        self._placeholder_poly = pv.Cube(
            center=(0.0, 0.0, side / 2),
            x_length=side,
            y_length=side,
            z_length=side,
        )
        self._placeholder_actor = self.plotter.add_mesh(
            self._placeholder_poly, color=PLACEHOLDER_COLOR, show_edges=False, reset_camera=False)
        self.status.setText("Reference cube · select GT and RM meshes to preview them.")
        self._refresh_floor()
        self.reset_view()

    def _remove_placeholder(self):
        if self._placeholder_actor is not None:
            self.plotter.remove_actor(self._placeholder_actor, render=False)
            self._placeholder_actor = None
            self._placeholder_poly = None

    def set_layer(self, key, mesh, scale=1.0):
        """Show ``mesh`` (trimesh) as layer ``key`` ('gt' | 'rm' | 'heatmap'); ``None`` removes the layer."""
        old = self._actors.pop(key, None)
        if old is not None:
            self.plotter.remove_actor(old, render=False)
        self._polys.pop(key, None)
        box = self._checks[key]
        if mesh is None:
            box.setEnabled(False)
            if not self._actors:
                self._show_placeholder()
            self._refresh_floor()
            self.plotter.render()
            return

        self._remove_placeholder()

        poly = to_polydata(mesh)
        if scale != 1.0:
            poly.points = poly.points * scale
        self._polys[key] = poly

        kwargs = dict(smooth_shading=False, show_edges=self.edges.isChecked(), reset_camera=False)
        if key == "heatmap" and "rgb" in poly.point_data:
            kwargs.update(scalars="rgb", rgb=True)
        else:
            kwargs.update(color=GT_COLOR if key == "gt" else RM_COLOR)
        if key == "rm":
            kwargs["opacity"] = self.opacity.value() / 100.0
        self._actors[key] = self.plotter.add_mesh(poly, **kwargs)

        box.setEnabled(True)
        was_blocked = box.blockSignals(True)
        box.setChecked(key != "heatmap" or "gt" not in self._actors)
        box.blockSignals(was_blocked)
        self._set_visible(key, box.isChecked())
        self._refresh_floor()
        self.reset_view()

    def _refresh_floor(self):
        """Create one horizontal grid plane beneath the current mesh bounds."""
        if self._floor_actor is not None:
            self.plotter.remove_actor(self._floor_actor, render=False)
            self._floor_actor = None
        bounds = self._scene_bounds()
        if bounds is None:
            return
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        diagonal = max(float(np.linalg.norm((xmax - xmin, ymax - ymin, zmax - zmin))), 1e-3)
        grid_size = max(diagonal * 4.0, 3.0)
        resolution = max(24, min(80, int(grid_size / max(diagonal * 0.16, 1e-3))))
        plane = pv.Plane(
            center=((xmin + xmax) / 2, (ymin + ymax) / 2, zmin - diagonal * 0.01),
            direction=(0.0, 0.0, 1.0),
            i_size=grid_size,
            j_size=grid_size,
            i_resolution=resolution,
            j_resolution=resolution,
        )
        self._floor_actor = self.plotter.add_mesh(
            plane,
            color=VIEW_BACKGROUND,
            show_edges=True,
            edge_color=GRID_COLOR,
            line_width=1.0,
            lighting=False,
            reset_camera=False,
        )

    def _scene_bounds(self):
        meshes = list(self._polys.values())
        if not meshes and self._placeholder_poly is not None:
            meshes.append(self._placeholder_poly)
        if not meshes:
            return None
        bounds = np.asarray([mesh.bounds for mesh in meshes], dtype=float)
        return (
            float(bounds[:, 0].min()), float(bounds[:, 1].max()),
            float(bounds[:, 2].min()), float(bounds[:, 3].max()),
            float(bounds[:, 4].min()), float(bounds[:, 5].max()),
        )

    def _camera_bounds(self):
        bounds = self._scene_bounds()
        if bounds is None or self._actors or self._placeholder_poly is None:
            return bounds
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        diagonal = float(np.linalg.norm((xmax - xmin, ymax - ymin, zmax - zmin)))
        half_extent = max(diagonal, 0.75)
        center_x, center_y = (xmin + xmax) / 2, (ymin + ymax) / 2
        return (
            center_x - half_extent, center_x + half_extent,
            center_y - half_extent, center_y + half_extent,
            zmin, zmax,
        )

    def show_run_result(self, gt_mesh, rm_mesh, heatmap_mesh, heatmap_scale):
        """Switch to the post-run view: aligned RM over GT, plus the heatmap (shown instead of the plain GT)."""
        self.set_layer("gt", gt_mesh)
        self.set_layer("rm", rm_mesh)
        self.set_layer("heatmap", heatmap_mesh, scale=heatmap_scale)
        if heatmap_mesh is not None:
            self._checks["heatmap"].setChecked(True)
            self._checks["gt"].setChecked(False)
            self._checks["rm"].setChecked(False)
        self.status.setText("Drag to rotate · right-drag or wheel to zoom · middle-drag to pan.")

    def _set_visible(self, key, visible):
        actor = self._actors.get(key)
        if actor is not None:
            actor.SetVisibility(bool(visible))
            self.plotter.render()

    def _on_opacity(self, value):
        actor = self._actors.get("rm")
        if actor is not None:
            actor.GetProperty().SetOpacity(value / 100.0)
            self.plotter.render()

    def _on_edges(self, checked):
        for actor in self._actors.values():
            actor.GetProperty().SetEdgeVisibility(bool(checked))
        self.plotter.render()

    def _save_screenshot(self):
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(self, "Save view", "view.png", "PNG (*.png)")
        if path:
            self.plotter.screenshot(path)


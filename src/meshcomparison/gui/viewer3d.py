"""Interactive 3D view (PyVista embedded in Qt) of the GT, the aligned RM and the deviation heatmap."""
import numpy as np
import pyvista as pv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget,
)
from pyvistaqt import QtInteractor


GT_COLOR = "#b8bec6"
RM_COLOR = "#e0793b"


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

        self.plotter = QtInteractor(self)
        self.plotter.set_background("#1e2227")
        self.plotter.add_axes()

        self._checks = {}
        controls = QHBoxLayout()
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
        reset.clicked.connect(self.plotter.reset_camera)
        controls.addWidget(reset)
        shot = QPushButton("Save image…")
        shot.clicked.connect(self._save_screenshot)
        controls.addWidget(shot)
        controls.addStretch(1)

        self.status = QLabel("Select the GT and RM files to preview them here.")
        self.status.setObjectName("hint")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self.plotter.interactor, 1)
        layout.addWidget(self.status)

    def close_plotter(self):
        self.plotter.close()

    def set_layer(self, key, mesh, scale=1.0):
        """Show ``mesh`` (trimesh) as layer ``key`` ('gt' | 'rm' | 'heatmap'); ``None`` removes the layer."""
        old = self._actors.pop(key, None)
        if old is not None:
            self.plotter.remove_actor(old, render=False)
        self._polys.pop(key, None)
        box = self._checks[key]
        if mesh is None:
            box.setEnabled(False)
            self.plotter.render()
            return

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
        self.plotter.reset_camera()

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


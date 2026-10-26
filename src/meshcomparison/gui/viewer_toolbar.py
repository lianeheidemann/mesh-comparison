# Controls above the 3D view: layer toggles, RM opacity, edges, heatmap palette, reset and screenshot buttons.
"""The widgets are public attributes; ``MeshViewer`` connects their signals."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QSlider


class ViewerToolbar(QFrame):
    def __init__(self, layers, parent=None):
        """``layers``: ``((key, label), ...)``; one disabled check box per layer, keyed in ``self.checks``."""
        super().__init__(parent)
        self.setObjectName("viewerToolbar")
        controls = QHBoxLayout(self)
        controls.setContentsMargins(10, 8, 10, 8)
        controls.setSpacing(10)

        self.checks = {}
        for key, label in layers:
            box = QCheckBox(label)
            box.setEnabled(False)
            self.checks[key] = box
            controls.addWidget(box)

        controls.addSpacing(12)
        controls.addWidget(QLabel("RM opacity"))
        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(10, 100)
        self.opacity.setValue(100)
        self.opacity.setFixedWidth(110)
        controls.addWidget(self.opacity)

        self.edges = QCheckBox("Edges")
        controls.addWidget(self.edges)

        self.exact_palette = QCheckBox("Exact palette")
        self.exact_palette.setToolTip(
            "Show the heatmap with the true RdYlGn_r colours of the legend, "
            "instead of the brighter look of the pipeline's PNG.")
        self.exact_palette.setEnabled(False)
        controls.addWidget(self.exact_palette)

        self.reset_button = QPushButton("Reset view")
        controls.addWidget(self.reset_button)
        self.screenshot_button = QPushButton("Save image…")
        controls.addWidget(self.screenshot_button)
        controls.addStretch(1)

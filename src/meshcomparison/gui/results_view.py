"""Metric tables and image gallery for the outputs of a run."""
import glob
import os

import pandas as pd
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QHeaderView, QLabel, QPushButton, QScrollArea, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)


def _fmt(value):
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _make_table(df, transpose=False):
    if transpose:
        df = df.T.reset_index()
        df.columns = ["parameter", "value"]
    table = QTableWidget(len(df), len(df.columns))
    table.setHorizontalHeaderLabels([str(c) for c in df.columns])
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    for r, row in enumerate(df.itertuples(index=False)):
        for c, value in enumerate(row):
            item = QTableWidgetItem(_fmt(value))
            if c > 0 or not transpose:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(r, c, item)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setStretchLastSection(True)
    return table


class ImageGallery(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._paths = []
        self._pixmap = None

        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(self._show)
        self.label = QLabel("No images yet.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.selector)
        layout.addWidget(self.scroll, 1)

    def set_images(self, paths):
        self._paths = list(paths)
        self.selector.blockSignals(True)
        self.selector.clear()
        for p in self._paths:
            self.selector.addItem(p[0], p[1])
        self.selector.blockSignals(False)
        if self._paths:
            self._show(0)
        else:
            self._pixmap = None
            self.label.setPixmap(QPixmap())
            self.label.setText("No images yet.")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()

    def _show(self, index):
        if index < 0 or index >= len(self._paths):
            return
        self._pixmap = QPixmap(self._paths[index][1])
        self._fit()

    def _fit(self):
        if self._pixmap is None or self._pixmap.isNull():
            return
        size = self.scroll.viewport().size()
        self.label.setPixmap(self._pixmap.scaled(
            size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


class ResultsView(QTabWidget):
    GEOMETRY_CSV = os.path.join("metrics", "metrics_geometry.csv")
    PERCEPTUAL_CSV = os.path.join("metrics", "metrics_perceptual.csv")
    PER_VIEW_CSV = os.path.join("metrics", "per_view_metrics.csv")
    METADATA_CSV = os.path.join("metrics", "run_metadata.csv")
    GEOMETRY_METADATA_CSV = os.path.join("metrics", "run_metadata_geometry.csv")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gallery = ImageGallery()
        self._out_dir = None
        self.open_button = QPushButton("Open output folder")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self._open_output)
        self.setCornerWidget(self.open_button, Qt.Corner.TopRightCorner)
        self._placeholder()

    def _open_output(self):
        if self._out_dir and os.path.isdir(self._out_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._out_dir))

    def _reset(self):
        pages = [self.widget(i) for i in range(self.count())]
        self.clear()
        for page in pages:
            if page is not self.gallery:
                page.deleteLater()

    def _placeholder(self):
        self._reset()
        empty = QLabel("Run an evaluation to see the metrics here.")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addTab(empty, "Results")

    def load(self, out_dir):
        """(Re)load every table and image that exists under ``out_dir``."""
        self._reset()
        self._out_dir = out_dir
        self.open_button.setEnabled(os.path.isdir(out_dir))
        added = False
        for title, rel, transpose in (
            ("Geometric metrics", self.GEOMETRY_CSV, True),
            ("Perceptual summary", self.PERCEPTUAL_CSV, False),
            ("Per-view metrics", self.PER_VIEW_CSV, False),
            ("Run metadata", self.METADATA_CSV, True),
            ("Run metadata (geometric)", self.GEOMETRY_METADATA_CSV, True),
        ):
            path = os.path.join(out_dir, rel)
            if os.path.isfile(path):
                self.addTab(_make_table(pd.read_csv(path), transpose=transpose), title)
                added = True

        images = []
        for pattern in ("renders/*.png", "heatmaps/*.png", "renders/pairs/*.png",
                        "renders/gt/*.png", "renders/rm/*.png"):
            for p in sorted(glob.glob(os.path.join(out_dir, pattern))):
                images.append((os.path.relpath(p, out_dir), p))
        if images:
            self.gallery.set_images(images)
            self.addTab(self.gallery, "Images")
            added = True

        if not added:
            self._placeholder()
        return added

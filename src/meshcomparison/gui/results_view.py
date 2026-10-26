"""Results tabs of a run: geometric and perceptual summaries, images and metric figures."""
import os

import pandas as pd
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QPushButton, QTabWidget

from .gallery import collect_figure_entries, collect_image_entries
from .image_gallery import ImageGallery
from .result_tables import make_geometry_page, make_summary_page


class ResultsView(QTabWidget):
    PERCEPTUAL_CSV = os.path.join("metrics", "metrics_perceptual.csv")
    GEOMETRY_CSV = os.path.join("metrics", "metrics_geometry.csv")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gallery = ImageGallery()
        self.figures = ImageGallery(columns=1)
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
            if page is not self.gallery and page is not self.figures:
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
        geometry = os.path.join(out_dir, self.GEOMETRY_CSV)
        geometry_df = pd.read_csv(geometry) if os.path.isfile(geometry) else None
        if geometry_df is not None and "region" in geometry_df.columns:  # folders of older versions lack it
            self.addTab(make_geometry_page(geometry_df), "Geometric summary")
            added = True
        summary = os.path.join(out_dir, self.PERCEPTUAL_CSV)
        if os.path.isfile(summary):
            self.addTab(make_summary_page(pd.read_csv(summary)), "Perceptual summary")
            added = True

        entries = collect_image_entries(out_dir)
        if entries:
            self.gallery.set_entries(entries)
            self.addTab(self.gallery, "Images")
            added = True

        figures = collect_figure_entries(out_dir)
        if figures:
            self.figures.set_entries(figures)
            self.addTab(self.figures, "Figures")
            added = True

        if not added:
            self._placeholder()
        return added

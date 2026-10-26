"""Metric tables and image gallery for the outputs of a run."""
import os

import pandas as pd
from PySide6.QtCore import QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QImageReader, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLabel, QPushButton, QScrollArea,
    QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from .gallery import collect_image_entries


SUMMARY_COLUMNS = (  # (CSV column, header) in reading order
    ("min", "Min"), ("p25", "25th pct"), ("median", "Median"), ("p75", "75th pct"), ("max", "Max"), ("mean", "Mean"),
)
METRIC_LABELS = {
    "lpips": ("LPIPS", "lower is better"),
    "psnr": ("PSNR (dB)", "higher is better"),
    "ssim": ("SSIM", "higher is better"),
}
GEOMETRY_ROWS = (  # (metrics_geometry.csv column, label, tooltip, format)
    ("chamfer_mean_gt_units", "Chamfer (GT units)", "lower is better; mean surface-sample distance", "{:.4g}"),
    ("hd95_gt_units", "HD95 (GT units)", "lower is better; 95th-percentile symmetric distance", "{:.4g}"),
    ("fscore_tau1pct", "F-score @1%", "higher is better; tolerance 1% of the GT diagonal", "{:.4f}"),
    ("fscore_tau2pct", "F-score @2%", "higher is better; tolerance 2% of the GT diagonal", "{:.4f}"),
    ("fscore_tau5pct", "F-score @5%", "higher is better; tolerance 5% of the GT diagonal", "{:.4f}"),
    ("normal_consistency", "Normal consistency", "higher is better; mean |cos| between matched surface normals",
     "{:.4f}"),
)
REGION_HEADERS = {"all": "Whole surface", "visible": "Visible", "hidden": "Hidden"}


def _new_table(n_rows, headers):
    """Read-only table in the results style (first column = metric name)."""
    table = QTableWidget(n_rows, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(46)
    return table


def _set_label(table, row, name, hint):
    label = QTableWidgetItem(name)
    label.setToolTip(hint)
    font = label.font()
    font.setBold(True)
    label.setFont(font)
    table.setItem(row, 0, label)


def _set_value(table, row, column, text):
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    table.setItem(row, column, item)


def _finish_table(table):
    """Evenly spaced, centred value columns and a height that fits every row."""
    header = table.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    header.setStretchLastSection(False)
    table.setFixedHeight(header.height() + table.verticalHeader().defaultSectionSize() * table.rowCount() + 8)
    return table


def _make_summary_table(df):
    """Perceptual summary: one row per metric, statistics as evenly spaced, centred columns."""
    columns = [(key, header) for key, header in SUMMARY_COLUMNS if key in df.columns]
    table = _new_table(len(df), ["Metric"] + [header for _, header in columns])
    for r, row in enumerate(df.to_dict("records")):
        name, hint = METRIC_LABELS.get(row["metric"], (str(row["metric"]).upper(), ""))
        _set_label(table, r, name, hint)
        for c, (key, _) in enumerate(columns, start=1):
            _set_value(table, r, c, f"{row[key]:.4f}")
    return _finish_table(table)


def _make_geometry_table(df):
    """Geometric summary: one row per metric, one column per GT region present in the CSV."""
    by_region = {row["region"]: row for row in df.to_dict("records")}
    regions = [r for r in REGION_HEADERS if r in by_region]
    headers = ["Metric"] + [
        REGION_HEADERS[r] if r == "all" else f"{REGION_HEADERS[r]} ({by_region[r]['gt_surface_fraction']:.0%})"
        for r in regions]
    rows = [entry for entry in GEOMETRY_ROWS if entry[0] in df.columns]
    table = _new_table(len(rows), headers)
    for r, (key, name, hint, fmt) in enumerate(rows):
        _set_label(table, r, name, hint)
        for c, region in enumerate(regions, start=1):
            value = by_region[region][key]
            _set_value(table, r, c, "n/a" if pd.isna(value) else fmt.format(value))
    return _finish_table(table)


def _make_page(table, hint_text):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)
    layout.addWidget(table)
    hint = QLabel(hint_text)
    hint.setObjectName("hint")
    hint.setWordWrap(True)
    layout.addWidget(hint)
    layout.addStretch(1)
    return page


def _make_summary_page(df):
    return _make_page(_make_summary_table(df),
                      "LPIPS: lower is better · PSNR: higher is better · SSIM: higher is better. "
                      "Statistics over all rendered views.")


def _make_geometry_page(df):
    first = df.iloc[0]
    if bool(first["alignment_triggered"]):
        alignment = f"Similarity ICP applied; uniform scale factor {first['icp_scale']:.4f}."
    else:
        alignment = "ICP not applied (pre-alignment MSE at or below the threshold)."
    regions = ("Visible / hidden: GT regions seen from the input view (share of the GT surface)."
               if len(df) > 1 else "Set an input view to split the metrics into visible / hidden regions.")
    return _make_page(_make_geometry_table(df),
                      f"Metrics on {int(first['n_samples']):,} area-uniform surface samples per mesh, after "
                      f"alignment. {alignment} {regions}")


class ImageGallery(QWidget):
    """GT/RM image pairs shown side by side; the default "All" mode stacks every pair vertically."""

    ALL_LABEL = "All"
    MARGIN = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []
        self._cells = []  # (QLabel, image path) of the images currently on screen

        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(self._render)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.content_layout.setSpacing(10)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content)

        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(120)
        self._resize_timer.timeout.connect(self._fit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.selector)
        layout.addWidget(self.scroll, 1)

    def set_entries(self, entries):
        """``entries``: ``[(title, [(caption, path), ...]), ...]`` as built by ``collect_image_entries``."""
        self._entries = list(entries)
        self.selector.blockSignals(True)
        self.selector.clear()
        self.selector.addItem(self.ALL_LABEL, None)
        for title, _images in self._entries:
            self.selector.addItem(title, title)
        self.selector.setCurrentIndex(0)
        self.selector.blockSignals(False)
        self._render()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start()

    def _clear(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self._cells = []

    def _render(self, _index=None):
        self._clear()
        selected = self.selector.currentData()
        shown = [e for e in self._entries if selected is None or e[0] == selected]
        if not shown:
            empty = QLabel("No images yet.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty)
            return
        for title, images in shown:
            header = QLabel(f"<b>{title}</b>")
            self.content_layout.addWidget(header)
            row = QHBoxLayout()
            row.setSpacing(10)
            for caption, path in images:
                column = QVBoxLayout()
                caption_label = QLabel(caption)
                caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_label = QLabel()
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                column.addWidget(caption_label)
                column.addWidget(image_label)
                row.addLayout(column, 1)
                self._cells.append((image_label, path))
            if len(images) == 1:
                row.addStretch(1)  # a lone image keeps the width of one pair column
            holder = QWidget()
            holder.setLayout(row)
            self.content_layout.addWidget(holder)
        self.content_layout.addStretch(1)
        self._fit()

    def _fit(self):
        """Scale each image to half the viewport width (and to the viewport height when only one pair is shown)."""
        if not self._cells:
            return
        viewport = self.scroll.viewport().size()
        width = max(120, (viewport.width() - 2 * self.MARGIN - 10) // 2 - 4)
        height = None if self.selector.currentData() is None else max(120, viewport.height() - 90)
        for label, path in self._cells:
            reader = QImageReader(path)
            size = reader.size()
            if not size.isValid():
                label.setText(f"Could not read {os.path.basename(path)}")
                continue
            scale = width / size.width()
            if height is not None:
                scale = min(scale, height / size.height())
            scale = min(scale, 1.0)
            reader.setScaledSize(QSize(max(1, round(size.width() * scale)), max(1, round(size.height() * scale))))
            label.setPixmap(QPixmap.fromImage(reader.read()))


class ResultsView(QTabWidget):
    PERCEPTUAL_CSV = os.path.join("metrics", "metrics_perceptual.csv")
    GEOMETRY_CSV = os.path.join("metrics", "metrics_geometry.csv")

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
        geometry = os.path.join(out_dir, self.GEOMETRY_CSV)
        geometry_df = pd.read_csv(geometry) if os.path.isfile(geometry) else None
        if geometry_df is not None and "region" in geometry_df.columns:  # folders of older versions lack it
            self.addTab(_make_geometry_page(geometry_df), "Geometric summary")
            added = True
        summary = os.path.join(out_dir, self.PERCEPTUAL_CSV)
        if os.path.isfile(summary):
            self.addTab(_make_summary_page(pd.read_csv(summary)), "Perceptual summary")
            added = True

        entries = collect_image_entries(out_dir)
        if entries:
            self.gallery.set_entries(entries)
            self.addTab(self.gallery, "Images")
            added = True

        if not added:
            self._placeholder()
        return added

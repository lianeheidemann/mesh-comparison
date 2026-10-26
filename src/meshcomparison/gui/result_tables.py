# Metric tables of the results view: geometric (per GT region) and perceptual summaries, with their notes.
"""Qt pages built from ``metrics_geometry.csv`` and ``metrics_perceptual.csv``."""
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .outputs import geometry_notes

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
    ("precision_tau1pct", "Precision @1%", "higher is better; share of RM samples within 1% of the GT surface "
     "(accuracy)", "{:.4f}"),
    ("recall_tau1pct", "Recall @1%", "higher is better; share of GT samples within 1% of the RM surface "
     "(completeness)", "{:.4f}"),
    ("fscore_tau1pct", "F-score @1%", "higher is better; tolerance 1% of the GT diagonal", "{:.4f}"),
    ("fscore_tau2pct", "F-score @2%", "higher is better; tolerance 2% of the GT diagonal", "{:.4f}"),
    ("fscore_tau5pct", "F-score @5%", "higher is better; tolerance 5% of the GT diagonal", "{:.4f}"),
    ("fscore_auc", "AUC-F", "higher is better; area under the F-score curve for τ from 0.5% to 10%", "{:.4f}"),
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


def _make_page(table, hint_text, warnings=()):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)
    for text in warnings:
        warning = QLabel(f"⚠ {text}")
        warning.setWordWrap(True)
        warning.setStyleSheet("background: #fff3cd; color: #664d03; border: 1px solid #ffda6a; "
                              "border-radius: 4px; padding: 6px;")
        layout.addWidget(warning)
    layout.addWidget(table)
    hint = QLabel(hint_text)
    hint.setObjectName("hint")
    hint.setWordWrap(True)
    layout.addWidget(hint)
    layout.addStretch(1)
    return page


def make_summary_page(df):
    """Perceptual summary tab: the statistics table and how to read it."""
    return _make_page(_make_summary_table(df),
                      "LPIPS: lower is better · PSNR: higher is better · SSIM: higher is better. "
                      "Statistics over all rendered views.")


def make_geometry_page(df):
    """Geometric summary tab: scene warnings, the per-region table and the run notes."""
    notes, warnings = geometry_notes(df)
    return _make_page(_make_geometry_table(df), "\n".join(notes), warnings)

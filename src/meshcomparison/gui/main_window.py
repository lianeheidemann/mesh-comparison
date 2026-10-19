import json
import os
import sys

import pandas as pd
from PySide6.QtCore import QProcess, QSettings, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QScrollArea,
    QGridLayout, QSpinBox, QSplitter, QTabWidget, QVBoxLayout, QWidget,
)

from ..common.device import CUDA_INSTALL_COMMAND, DeviceInfo
from ..common.io import load_mesh
from .config import MESH_FILE_FILTER, RunConfig, validate
from .results_view import ResultsView
from .runner import PipelineRunner
from .viewer3d import MeshViewer


class FileField(QWidget):
    def __init__(self, caption, directory=False, parent=None):
        super().__init__(parent)
        self._caption = caption
        self._directory = directory
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Select…")
        button = QPushButton("Browse…")
        button.clicked.connect(self._browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.edit, 1)
        layout.addWidget(button)

    def text(self):
        return self.edit.text().strip()

    def setText(self, value):
        self.edit.setText(value)

    def _browse(self):
        start = self.text() or QSettings().value("last_dir", "")
        if self._directory:
            path = QFileDialog.getExistingDirectory(self, self._caption, start)
        else:
            path, _ = QFileDialog.getOpenFileName(self, self._caption, start, MESH_FILE_FILTER)
        if path:
            QSettings().setValue("last_dir", os.path.dirname(path) if not self._directory else path)
            self.edit.setText(path)


def _spin(minimum, maximum, value, decimals=None, step=None, suffix=""):
    box = QDoubleSpinBox() if decimals is not None else QSpinBox()
    if decimals is not None:
        box.setDecimals(decimals)
    box.setRange(minimum, maximum)
    box.setValue(value)
    if step is not None:
        box.setSingleStep(step)
    if suffix:
        box.setSuffix(suffix)
    return box


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesh Comparison")
        self.resize(1400, 860)

        self.runner = PipelineRunner(self)
        self.runner.log.connect(self._append_log)
        self.runner.progress.connect(self._on_progress)
        self.runner.finished.connect(self._on_finished)

        self._last_cfg = None
        self._device_process = None
        self._device_info = None

        self.viewer = MeshViewer()
        self.results = ResultsView()
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(5000)
        self.log_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        mono = self.log_view.font()
        mono.setFamily("Consolas" if sys.platform == "win32" else "monospace")
        self.log_view.setFont(mono)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.viewer, "3D view")
        self.tabs.addTab(self.results, "Results")
        self.tabs.addTab(self.log_view, "Log")

        splitter = QSplitter()
        splitter.addWidget(self._build_side_panel())
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 1000])
        splitter.setChildrenCollapsible(False)
        self.setCentralWidget(splitter)

        self.statusBar().showMessage("Ready")
        self._detect_device()

    # ---- construction -------------------------------------------------

    def _build_side_panel(self):
        panel = QWidget()
        panel.setObjectName("sidePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        heading = QLabel("Evaluate meshes")
        heading.setObjectName("panelHeading")
        subtitle = QLabel("Compare geometry and visual similarity")
        subtitle.setObjectName("panelSubtitle")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        files = QGroupBox("Meshes")
        files.setObjectName("card")
        form = QFormLayout(files)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(6)
        self.gt_field = FileField("Select ground-truth mesh")
        self.rm_field = FileField("Select reconstructed mesh")
        self.out_field = FileField("Select output folder", directory=True)
        self.out_field.setText(os.path.abspath("output"))
        form.addRow("Ground truth (GT)", self.gt_field)
        form.addRow("Reconstruction (RM)", self.rm_field)
        form.addRow("Output folder", self.out_field)
        note = QLabel("STL, OBJ, PLY, OFF, GLB/GLTF. FBX is not supported: convert it first.")
        note.setObjectName("hint")
        note.setWordWrap(True)
        form.addRow(note)
        layout.addWidget(files)
        self.gt_field.edit.editingFinished.connect(lambda: self._preview("gt"))
        self.rm_field.edit.editingFinished.connect(lambda: self._preview("rm"))

        pipelines = QGroupBox("Pipelines")
        pipelines.setObjectName("card")
        pl = QVBoxLayout(pipelines)
        pl.setSpacing(7)
        self.geometry_check = QCheckBox("Geometric (Chamfer, Hausdorff, RMSE, heatmap)")
        self.perceptual_check = QCheckBox("Perceptual (LPIPS, PSNR, SSIM over multiple views)")
        self.geometry_check.setChecked(True)
        self.perceptual_check.setChecked(True)
        pl.addWidget(self.geometry_check)
        pl.addWidget(self.perceptual_check)
        layout.addWidget(pipelines)

        defaults = RunConfig()
        params = QGroupBox("Parameters")
        params.setObjectName("card")
        pf = QGridLayout(params)
        pf.setContentsMargins(10, 8, 10, 8)
        pf.setHorizontalSpacing(8)
        pf.setVerticalSpacing(6)
        self.mse = QLineEdit(repr(defaults.mse_threshold))
        self.mse.setToolTip("Normalized symmetric MSE above which similarity ICP alignment runs")
        self.azimuth = _spin(-360, 360, defaults.azimuth, decimals=3, suffix=" °")
        self.elevation = _spin(-90, 90, defaults.elevation, decimals=3, suffix=" °")
        self.width = _spin(64, 8192, defaults.width, suffix=" px")
        self.height = _spin(64, 8192, defaults.height, suffix=" px")
        self.num_views = _spin(1, 1000, defaults.num_views)
        self.margin = _spin(0.5, 3.0, defaults.camera_margin, decimals=3, step=0.01)
        self.radius = _spin(0.5, 10.0, defaults.radius_factor, decimals=3, step=0.05)
        # Fixed for now so runs stay comparable; values come from RunConfig defaults.
        self.mse.setReadOnly(True)
        for box in (self.azimuth, self.elevation, self.width, self.height,
                    self.num_views, self.margin, self.radius):
            box.setReadOnly(True)
            box.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            box.setToolTip("Fixed value (not editable)")
        parameters = (
            ("ICP threshold", self.mse, "MSE threshold used to decide whether ICP alignment runs."),
            ("Azimuth", self.azimuth, "Geometric render camera azimuth."),
            ("Elevation", self.elevation, "Geometric render camera elevation."),
            ("Views", self.num_views, "Number of views used for perceptual evaluation."),
            ("Width", self.width, "Perceptual render width."),
            ("Height", self.height, "Perceptual render height."),
            ("Camera margin", self.margin, "Camera framing margin."),
            ("Radius factor", self.radius, "Camera radius factor."),
        )
        for index, (caption, control, tooltip) in enumerate(parameters):
            row, pair = divmod(index, 2)
            label = QLabel(caption)
            label.setObjectName("parameterLabel")
            label.setToolTip(tooltip)
            control.setToolTip(tooltip)
            pf.addWidget(label, row, pair * 2)
            value = QLabel(control.text())
            value.setObjectName("parameterValue")
            value.setToolTip(tooltip)
            control.hide()
            pf.addWidget(control, row, pair * 2 + 1)
            pf.addWidget(value, row, pair * 2 + 1)
        pf.setColumnStretch(1, 1)
        pf.setColumnStretch(3, 1)
        layout.addWidget(params)

        device = QGroupBox("Compute device (LPIPS)")
        device.setObjectName("card")
        dl = QVBoxLayout(device)
        dl.setSpacing(6)
        self.device_combo = QComboBox()
        self.device_combo.addItem("Auto — prefer CUDA", "auto")
        self.device_combo.addItem("CUDA only", "cuda")
        self.device_combo.addItem("CPU only", "cpu")
        self.device_label = QLabel("Detecting…")
        self.device_label.setWordWrap(True)
        self.device_warning = QLabel()
        self.device_warning.setObjectName("warning")
        self.device_warning.setWordWrap(True)
        self.device_warning.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.device_warning.hide()
        self.copy_install_button = QPushButton("Copy CUDA install command")
        self.copy_install_button.clicked.connect(self._copy_install_command)
        self.copy_install_button.hide()
        dl.addWidget(self.device_combo)
        dl.addWidget(self.device_label)
        dl.addWidget(self.device_warning)
        dl.addWidget(self.copy_install_button)
        layout.addWidget(device)

        self.run_button = QPushButton("Run evaluation")
        self.run_button.setObjectName("primary")
        self.run_button.clicked.connect(self._run)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.runner.cancel)
        self.open_button = QPushButton("Open output folder")
        self.open_button.clicked.connect(self._open_output)
        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button, 1)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)
        layout.addWidget(self.open_button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("hint")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress)
        layout.addWidget(self.progress_label)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(panel)
        scroll.setMinimumWidth(380)
        return scroll

    # ---- device detection --------------------------------------------

    def _detect_device(self):
        process = QProcess(self)
        process.finished.connect(self._on_device_detected)
        self._device_process = process
        process.start(sys.executable, ["-m", "meshcomparison.common.device"])

    def _on_device_detected(self, exit_code, _status):
        out = bytes(self._device_process.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
        self._device_process = None
        try:
            info = DeviceInfo(**json.loads(out.splitlines()[-1]))
        except (ValueError, TypeError, IndexError):
            self.device_label.setText("Could not detect the compute device.")
            return
        self._device_info = info
        self.device_label.setText(f"Detected: {info.describe()}" + (
            f" · PyTorch {info.torch_version} (CUDA {info.torch_cuda_version})" if info.torch_version else ""))
        if info.warning:
            self.device_warning.setText(info.warning)
            self.device_warning.show()
        else:
            self.device_warning.hide()
        cpu_only_torch = info.nvidia_gpu_detected and info.torch_version and info.torch_cuda_version is None
        self.copy_install_button.setVisible(bool(cpu_only_torch))

    def _copy_install_command(self):
        QApplication.clipboard().setText(CUDA_INSTALL_COMMAND)
        self.statusBar().showMessage("CUDA install command copied to the clipboard.", 5000)

    # ---- actions ------------------------------------------------------

    def _config(self):
        try:
            mse = float(self.mse.text())
        except ValueError:
            mse = float("nan")
        return RunConfig(
            gt=self.gt_field.text(), rm=self.rm_field.text(), out=self.out_field.text(),
            run_geometry=self.geometry_check.isChecked(), run_perceptual=self.perceptual_check.isChecked(),
            mse_threshold=mse, azimuth=self.azimuth.value(), elevation=self.elevation.value(),
            width=self.width.value(), height=self.height.value(), num_views=self.num_views.value(),
            camera_margin=self.margin.value(), radius_factor=self.radius.value(),
            device=self.device_combo.currentData(),
        )

    def _preview(self, which):
        path = (self.gt_field if which == "gt" else self.rm_field).text()
        if not path or not os.path.isfile(path) or path.lower().endswith(".fbx"):
            self.viewer.set_layer(which, None)
            return
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
            self.viewer.set_layer(which, load_mesh(path))
            self.tabs.setCurrentWidget(self.viewer)
        except Exception as exc:
            QMessageBox.warning(self, "Could not load mesh", str(exc))
        finally:
            QApplication.restoreOverrideCursor()

    def _run(self):
        cfg = self._config()
        errors = validate(cfg)
        if cfg.mse_threshold != cfg.mse_threshold:  # NaN
            errors.append("MSE threshold is not a valid number.")
        if errors:
            QMessageBox.warning(self, "Cannot run", "\n".join(errors))
            return
        os.makedirs(cfg.out, exist_ok=True)
        self._last_cfg = cfg
        self.log_view.clear()
        self.tabs.setCurrentWidget(self.log_view)
        self._set_running(True)
        self.runner.start(cfg)

    def _set_running(self, running):
        self.run_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        if running:
            self.progress.setValue(0)

    def _append_log(self, text):
        self.log_view.appendPlainText(text)

    def _on_progress(self, percent, label):
        self.progress.setValue(percent)
        self.progress_label.setText(label)

    def _on_finished(self, success, message):
        self._set_running(False)
        self.statusBar().showMessage(message, 8000)
        self.progress_label.setText(message)
        self._append_log(f"\n{message}")
        if not success:
            if "cancelled" not in message:
                QMessageBox.critical(self, "Evaluation failed", message)
            return
        cfg = self._last_cfg
        self.results.load(cfg.out)
        self._show_result_3d(cfg)
        self.tabs.setCurrentWidget(self.viewer)

    def _show_result_3d(self, cfg):
        try:
            gt = load_mesh(cfg.gt)
            aligned = os.path.join(cfg.out, "aligned", "rm_aligned.ply")
            rm = load_mesh(aligned) if os.path.isfile(aligned) else None
            heat = None
            scale = 1.0
            vmax = None
            heat_path = os.path.join(cfg.out, "heatmaps", "gt_heatmap_colored.ply")
            meta_path = os.path.join(cfg.out, "metrics", "run_metadata.csv")
            if cfg.run_geometry and os.path.isfile(heat_path):
                heat = load_mesh(heat_path)
                # the heatmap mesh is exported in the internally normalized scale (GT bbox diagonal = 1)
                geometry_csv = os.path.join(cfg.out, "metrics", "metrics_geometry.csv")
                for csv in (geometry_csv, meta_path):
                    if os.path.isfile(csv):
                        row = pd.read_csv(csv)
                        if "gt_bbox_diagonal_original_units" in row:
                            scale = float(row["gt_bbox_diagonal_original_units"].iloc[0])
                            break
                geometry_meta = os.path.join(cfg.out, "metrics", "run_metadata_geometry.csv")
                if os.path.isfile(geometry_meta):
                    row = pd.read_csv(geometry_meta)
                    if "heatmap_vmax_gt_units" in row:
                        vmax = float(row["heatmap_vmax_gt_units"].iloc[0])
            self.viewer.show_run_result(gt, rm, heat, scale, vmax)
        except Exception as exc:
            self._append_log(f"Could not display the 3D result: {exc}")

    def _open_output(self):
        out = self.out_field.text()
        if out and os.path.isdir(out):
            QDesktopServices.openUrl(QUrl.fromLocalFile(out))

    def closeEvent(self, event):
        if self.runner.running:
            self.runner.cancel()
        self.viewer.close_plotter()
        super().closeEvent(event)

# Scrollable gallery of a run's images (GT/RM pairs side by side) and metric figures (full width).
"""Image gallery widget; entries come from ``gallery.collect_image_entries`` / ``collect_figure_entries``."""
import os

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class ImageGallery(QWidget):
    """Images in rows of ``columns`` (GT/RM pairs side by side; figures at full width with ``columns=1``); the
    default "All" mode stacks every entry vertically."""

    ALL_LABEL = "All"
    MARGIN = 12

    def __init__(self, parent=None, columns=2):
        super().__init__(parent)
        self.columns = columns
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
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)
            for caption, path in images:
                column = QVBoxLayout()
                if caption:
                    caption_label = QLabel(caption)
                    caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    column.addWidget(caption_label)
                image_label = QLabel()
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                column.addWidget(image_label)
                row.addLayout(column, 1)
                self._cells.append((image_label, path))
            if len(images) < self.columns:
                row.addStretch(self.columns - len(images))  # a lone image keeps the width of one column
            holder = QWidget()
            holder.setLayout(row)
            self.content_layout.addWidget(holder)
        self.content_layout.addStretch(1)
        self._fit()

    def _fit(self):
        """Scale each image to its share of the viewport width (and to the viewport height when one entry is shown)."""
        if not self._cells:
            return
        viewport = self.scroll.viewport().size()
        bar = self.scroll.verticalScrollBar()
        available = viewport.width() - (0 if bar.isVisible() else bar.sizeHint().width())  # room for a late bar
        spacing = 10 * (self.columns - 1)
        width = max(120, (available - 2 * self.MARGIN - spacing) // self.columns - 4)
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

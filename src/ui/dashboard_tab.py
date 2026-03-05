"""
Dashboard tab: live bandwidth charts + stat cards.
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSlot
import pyqtgraph as pg
import numpy as np

from core.network_monitor import NetworkMonitor


def _make_card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("Card")
    return f


class StatCard(QFrame):
    def __init__(self, label: str, unit: str = "", color: str = "#a78bfa",
                 parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumWidth(160)
        lay = QVBoxLayout(self)
        lay.setSpacing(2)
        lay.setContentsMargins(16, 14, 16, 14)

        self.val_lbl = QLabel("0")
        self.val_lbl.setObjectName("StatValue")
        self.val_lbl.setStyleSheet(f"color: {color};")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.unit_lbl = QLabel(unit)
        self.unit_lbl.setObjectName("SubLabel")
        self.unit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_lbl = QLabel(label.upper())
        top_lbl.setObjectName("StatLabel")
        top_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(top_lbl)
        lay.addWidget(self.val_lbl)
        lay.addWidget(self.unit_lbl)

    def set_value(self, text: str, unit: str = ""):
        self.val_lbl.setText(text)
        if unit:
            self.unit_lbl.setText(unit)


class DashboardTab(QWidget):
    def __init__(self, monitor: NetworkMonitor, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self._chart_type = "line"  # or "bar"
        self._dark = True
        self._setup_ui()
        monitor.stats_updated.connect(self._on_stats)

    # ── UI ─────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Top controls row ──
        ctrl = QHBoxLayout()

        iface_lbl = QLabel("Interface:")
        iface_lbl.setObjectName("SubLabel")
        self.iface_combo = QComboBox()
        self.iface_combo.addItems(NetworkMonitor.get_interfaces())
        self.iface_combo.currentTextChanged.connect(self.monitor.set_interface)

        chart_lbl = QLabel("Chart:")
        chart_lbl.setObjectName("SubLabel")
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Line Chart", "Bar Chart"])
        self.chart_combo.currentIndexChanged.connect(self._on_chart_type)

        ctrl.addWidget(iface_lbl)
        ctrl.addWidget(self.iface_combo)
        ctrl.addSpacing(20)
        ctrl.addWidget(chart_lbl)
        ctrl.addWidget(self.chart_combo)
        ctrl.addStretch()
        root.addLayout(ctrl)

        # ── Stat cards ──
        cards_lay = QHBoxLayout()
        cards_lay.setSpacing(10)

        self.card_dl   = StatCard("Download",    color="#06b6d4")
        self.card_ul   = StatCard("Upload",      color="#f59e0b")
        self.card_pkts = StatCard("Packets/s",   color="#a78bfa")
        self.card_conn = StatCard("Connections", color="#10b981")

        for c in (self.card_dl, self.card_ul, self.card_pkts, self.card_conn):
            cards_lay.addWidget(c)
        root.addLayout(cards_lay)

        # ── Charts ──
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)

        # Download chart
        self.dl_plot = self._make_plot(title="Download Speed", color="#06b6d4")
        dl_card = _make_card()
        dl_lay = QVBoxLayout(dl_card)
        dl_lay.setContentsMargins(8, 8, 8, 8)
        dl_lay.addWidget(QLabel("⬇  Download Speed", objectName="SectionTitle"))
        dl_lay.addWidget(self.dl_plot)
        charts_row.addWidget(dl_card)

        # Upload chart
        self.ul_plot = self._make_plot(title="Upload Speed", color="#f59e0b")
        ul_card = _make_card()
        ul_lay = QVBoxLayout(ul_card)
        ul_lay.setContentsMargins(8, 8, 8, 8)
        ul_lay.addWidget(QLabel("⬆  Upload Speed", objectName="SectionTitle"))
        ul_lay.addWidget(self.ul_plot)
        charts_row.addWidget(ul_card)

        root.addLayout(charts_row)

        # ── Combined chart ──
        combo_card = _make_card()
        combo_lay = QVBoxLayout(combo_card)
        combo_lay.setContentsMargins(8, 8, 8, 8)
        combo_lay.addWidget(QLabel("📊  Combined Traffic", objectName="SectionTitle"))
        self.combo_plot = self._make_plot_combined()
        combo_lay.addWidget(self.combo_plot)
        root.addWidget(combo_card)

        # pyqtgraph curves
        self._dl_curve = self.dl_plot.plot(pen=pg.mkPen("#06b6d4", width=2))
        self._ul_curve = self.ul_plot.plot(pen=pg.mkPen("#f59e0b", width=2))
        self._combo_dl = self.combo_plot.plot(pen=pg.mkPen("#06b6d4", width=2),
                                              name="Download")
        self._combo_ul = self.combo_plot.plot(pen=pg.mkPen("#f59e0b", width=2),
                                              name="Upload")

        # Bar item placeholders
        self._bar_dl = None
        self._bar_ul = None

    def _make_plot(self, title: str, color: str) -> pg.PlotWidget:
        pw = pg.PlotWidget()
        pw.setBackground("#0f1629" if self._dark else "#ffffff")
        pw.showGrid(x=False, y=True, alpha=0.15)
        pw.getAxis("left").setTextPen("#94a3b8")
        pw.getAxis("bottom").setTextPen("#94a3b8")
        pw.setLabel("left", "Speed", units="B/s")
        pw.getAxis("left").setStyle(tickFont=self._small_font())
        pw.setMinimumHeight(160)
        # Fill under curve
        pw.setXRange(0, 120, padding=0)
        return pw

    def _make_plot_combined(self) -> pg.PlotWidget:
        pw = pg.PlotWidget()
        pw.setBackground("#0f1629" if self._dark else "#ffffff")
        pw.showGrid(x=False, y=True, alpha=0.15)
        pw.getAxis("left").setTextPen("#94a3b8")
        pw.getAxis("bottom").setTextPen("#94a3b8")
        pw.setLabel("left", "Speed", units="B/s")
        pw.setMinimumHeight(180)
        pw.addLegend()
        pw.setXRange(0, 120, padding=0)
        return pw

    @staticmethod
    def _small_font():
        from PyQt6.QtGui import QFont
        f = QFont()
        f.setPointSize(8)
        return f

    # ── slots ──────────────────────────────────────────────────────────────

    @pyqtSlot(dict)
    def _on_stats(self, stats: dict):
        dl_h = np.array(stats["dl_history"], dtype=float)
        ul_h = np.array(stats["ul_history"], dtype=float)
        x = np.arange(len(dl_h))

        if self._chart_type == "line":
            self._dl_curve.setData(x, dl_h)
            self._ul_curve.setData(x, ul_h)
            self._combo_dl.setData(x, dl_h)
            self._combo_ul.setData(x, ul_h)
        else:
            self._update_bars(x, dl_h, ul_h)

        # Stat cards
        dl_s = stats["dl_speed"]
        ul_s = stats["ul_speed"]
        self.card_dl.set_value(
            *self._split_speed(dl_s)
        )
        self.card_ul.set_value(
            *self._split_speed(ul_s)
        )
        pps = stats["packets_recv_ps"] + stats["packets_sent_ps"]
        self.card_pkts.set_value(f"{pps:.0f}", "pkt/s")
        self.card_conn.set_value(str(stats["conn_count"]))

    def _update_bars(self, x, dl_h, ul_h):
        # Remove old bars
        for old in (self._bar_dl, self._bar_ul):
            if old and old.scene():
                self.dl_plot.removeItem(old) if old in self.dl_plot.items() else None
                self.ul_plot.removeItem(old) if old in self.ul_plot.items() else None
                self.combo_plot.removeItem(old) if old in self.combo_plot.items() else None

        step = 4
        xs = x[::step]
        dl_s = dl_h[::step]
        ul_s = ul_h[::step]

        self._bar_dl = pg.BarGraphItem(x=xs, height=dl_s, width=0.7,
                                       brush="#06b6d4")
        self.dl_plot.addItem(self._bar_dl)

        self._bar_ul = pg.BarGraphItem(x=xs, height=ul_s, width=0.7,
                                       brush="#f59e0b")
        self.ul_plot.addItem(self._bar_ul)

    @staticmethod
    def _split_speed(bps: float) -> tuple[str, str]:
        if bps >= 1_000_000_000:
            return f"{bps/1_000_000_000:.2f}", "GB/s"
        if bps >= 1_000_000:
            return f"{bps/1_000_000:.2f}", "MB/s"
        if bps >= 1_000:
            return f"{bps/1_000:.1f}", "KB/s"
        return f"{bps:.0f}", "B/s"

    def _on_chart_type(self, idx: int):
        self._chart_type = "line" if idx == 0 else "bar"
        # Show/hide line curves
        vis = self._chart_type == "line"
        for curve in (self._dl_curve, self._ul_curve,
                      self._combo_dl, self._combo_ul):
            curve.setVisible(vis)

    def apply_theme(self, dark: bool):
        self._dark = dark
        bg = "#0f1629" if dark else "#ffffff"
        for pw in (self.dl_plot, self.ul_plot, self.combo_plot):
            pw.setBackground(bg)

"""
Statistics tab: historical bandwidth charts and period summaries.
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QGridLayout, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
import pyqtgraph as pg
import numpy as np

from core.db_manager import DBManager
from core.export_manager import ExportManager
from core.network_monitor import NetworkMonitor


def _card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("Card")
    return f


def _fmt(b: int) -> str:
    return NetworkMonitor.format_bytes(b)


class StatBlock(QFrame):
    def __init__(self, label: str, color: str = "#a78bfa", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(2)

        lbl = QLabel(label.upper())
        lbl.setObjectName("StatLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.val = QLabel("—")
        self.val.setObjectName("StatValue")
        self.val.setStyleSheet(f"color: {color};")
        self.val.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(lbl)
        lay.addWidget(self.val)

    def set(self, text: str):
        self.val.setText(text)


class StatisticsTab(QWidget):
    def __init__(self, db: DBManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.exporter = ExportManager(db)
        self._period = "month"
        self._dark = True
        self._setup_ui()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)
        self._refresh_timer.start(60_000)  # refresh every minute
        self._refresh()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Controls ──
        ctrl = QHBoxLayout()

        period_lbl = QLabel("Period:")
        period_lbl.setObjectName("SubLabel")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "Week", "Month", "Year", "All Time"])
        self.period_combo.setCurrentIndex(2)
        self.period_combo.currentIndexChanged.connect(self._on_period)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setObjectName("BtnSecondary")
        refresh_btn.clicked.connect(self._refresh)

        export_csv = QPushButton("⬇  CSV")
        export_csv.setObjectName("BtnSecondary")
        export_csv.clicked.connect(lambda: self._export("csv"))

        export_json = QPushButton("⬇  JSON")
        export_json.setObjectName("BtnSecondary")
        export_json.clicked.connect(lambda: self._export("json"))

        export_pdf = QPushButton("⬇  PDF")
        export_pdf.clicked.connect(lambda: self._export("pdf"))

        ctrl.addWidget(period_lbl)
        ctrl.addWidget(self.period_combo)
        ctrl.addSpacing(16)
        ctrl.addWidget(refresh_btn)
        ctrl.addStretch()
        ctrl.addWidget(export_csv)
        ctrl.addWidget(export_json)
        ctrl.addWidget(export_pdf)
        root.addLayout(ctrl)

        # ── Summary cards ──
        summary = QHBoxLayout()
        summary.setSpacing(10)
        self.blk_dl      = StatBlock("Total Download",  "#06b6d4")
        self.blk_ul      = StatBlock("Total Upload",    "#f59e0b")
        self.blk_total   = StatBlock("Combined",        "#a78bfa")
        self.blk_peak_dl = StatBlock("Peak DL Speed",   "#10b981")
        self.blk_avg_dl  = StatBlock("Avg DL Speed",    "#94a3b8")
        for b in (self.blk_dl, self.blk_ul, self.blk_total,
                  self.blk_peak_dl, self.blk_avg_dl):
            summary.addWidget(b)
        root.addLayout(summary)

        # ── Daily chart ──
        chart_card = _card()
        chart_lay = QVBoxLayout(chart_card)
        chart_lay.setContentsMargins(8, 8, 8, 8)
        chart_lay.addWidget(QLabel("📈  Daily Usage", objectName="SectionTitle"))

        self.daily_plot = pg.PlotWidget()
        self.daily_plot.setBackground("#0f1629")
        self.daily_plot.showGrid(x=False, y=True, alpha=0.15)
        self.daily_plot.setLabel("left", "Bytes")
        self.daily_plot.setMinimumHeight(220)
        self.daily_plot.addLegend()
        chart_lay.addWidget(self.daily_plot)
        root.addWidget(chart_card)

        self._dl_bars: pg.BarGraphItem | None = None
        self._ul_bars: pg.BarGraphItem | None = None

    # ── refresh ────────────────────────────────────────────────────────────

    def _refresh(self):
        agg = self.db.get_aggregated_usage(self._period)
        self.blk_dl.set(_fmt(agg["dl"]))
        self.blk_ul.set(_fmt(agg["ul"]))
        self.blk_total.set(_fmt(agg["dl"] + agg["ul"]))
        self.blk_peak_dl.set(
            f"{agg['peak_dl']/1e6:.2f} MB/s" if agg["peak_dl"] else "—"
        )
        self.blk_avg_dl.set(
            f"{agg['avg_dl']/1_000:.1f} KB/s" if agg["avg_dl"] else "—"
        )

        days_map = {"today": 1, "week": 7, "month": 30,
                    "year": 365, "alltime": 3650}
        rows = self.db.get_daily_usage(days=days_map.get(self._period, 30))

        if rows:
            xs = np.arange(len(rows))
            dl_vals = np.array([r["dl"] for r in rows], dtype=float)
            ul_vals = np.array([r["ul"] for r in rows], dtype=float)

            self.daily_plot.clear()
            self.daily_plot.addLegend()

            dl_b = pg.BarGraphItem(x=xs - 0.2, height=dl_vals,
                                   width=0.4, brush="#06b6d4", name="Download")
            ul_b = pg.BarGraphItem(x=xs + 0.2, height=ul_vals,
                                   width=0.4, brush="#f59e0b", name="Upload")
            self.daily_plot.addItem(dl_b)
            self.daily_plot.addItem(ul_b)

            # X axis date labels
            if len(rows) <= 31:
                ticks = [(i, r["date"][-5:]) for i, r in enumerate(rows)]
                self.daily_plot.getAxis("bottom").setTicks([ticks])
        else:
            self.daily_plot.clear()
            self.daily_plot.addItem(
                pg.TextItem("No data yet — start monitoring to collect statistics",
                             color="#64748b")
            )

    def _on_period(self, idx: int):
        periods = ["today", "week", "month", "year", "alltime"]
        self._period = periods[idx]
        self._refresh()

    # ── export ─────────────────────────────────────────────────────────────

    def _export(self, fmt: str):
        ext = {"csv": "CSV Files (*.csv)", "json": "JSON Files (*.json)",
               "pdf": "PDF Files (*.pdf)"}[fmt]
        path, _ = QFileDialog.getSaveFileName(
            self, f"Export {fmt.upper()}", f"network_report_{self._period}.{fmt}",
            ext
        )
        if not path:
            return
        try:
            if fmt == "csv":
                self.exporter.export_csv(self._period, path)
            elif fmt == "json":
                self.exporter.export_json(self._period, path)
            elif fmt == "pdf":
                self.exporter.export_pdf(self._period, path)
            QMessageBox.information(self, "Export Complete",
                                    f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def apply_theme(self, dark: bool):
        self._dark = dark
        self.daily_plot.setBackground("#0f1629" if dark else "#ffffff")

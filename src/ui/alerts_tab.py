"""
Alerts tab: configure thresholds and view alert history.
"""

import time
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QGroupBox, QDoubleSpinBox, QCheckBox,
    QHeaderView, QAbstractItemView, QSplitter,
    QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor

from core.db_manager import DBManager
from core.alert_manager import AlertManager


class AlertsTab(QWidget):
    def __init__(self, db: DBManager, alert_mgr: AlertManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.alert_mgr = alert_mgr
        self._dark = True
        self._setup_ui()
        self._load_config()
        self._load_history()

        alert_mgr.alert_fired.connect(self._on_alert)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        root.addWidget(QLabel("🔔  Alerts & Notifications",
                               objectName="SectionTitle"))

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: config ──
        config_w = QWidget()
        config_lay = QVBoxLayout(config_w)
        config_lay.setContentsMargins(0, 0, 0, 0)
        config_lay.setSpacing(12)

        # Bandwidth limits
        bw_box = QGroupBox("Bandwidth Thresholds")
        bw_form = QFormLayout(bw_box)

        self.dl_limit = QDoubleSpinBox()
        self.dl_limit.setRange(0, 10_000)
        self.dl_limit.setSuffix(" MB/s  (0 = off)")
        self.dl_limit.setDecimals(1)
        bw_form.addRow("Download Limit:", self.dl_limit)

        self.ul_limit = QDoubleSpinBox()
        self.ul_limit.setRange(0, 10_000)
        self.ul_limit.setSuffix(" MB/s  (0 = off)")
        self.ul_limit.setDecimals(1)
        bw_form.addRow("Upload Limit:", self.ul_limit)

        self.spike_factor = QDoubleSpinBox()
        self.spike_factor.setRange(1.5, 20.0)
        self.spike_factor.setSingleStep(0.5)
        self.spike_factor.setValue(3.0)
        self.spike_factor.setSuffix("×  average")
        bw_form.addRow("Spike Threshold:", self.spike_factor)

        config_lay.addWidget(bw_box)

        # Usage limits
        usage_box = QGroupBox("Usage Limits (Notifications)")
        usage_form = QFormLayout(usage_box)

        self.daily_limit = QDoubleSpinBox()
        self.daily_limit.setRange(0, 100_000)
        self.daily_limit.setSuffix(" MB  (0 = off)")
        self.daily_en = QCheckBox("Enabled")
        r1 = QHBoxLayout()
        r1.addWidget(self.daily_limit)
        r1.addWidget(self.daily_en)
        usage_form.addRow("Daily:", r1)

        self.monthly_limit = QDoubleSpinBox()
        self.monthly_limit.setRange(0, 100_000_000)
        self.monthly_limit.setSuffix(" MB  (0 = off)")
        self.monthly_en = QCheckBox("Enabled")
        r2 = QHBoxLayout()
        r2.addWidget(self.monthly_limit)
        r2.addWidget(self.monthly_en)
        usage_form.addRow("Monthly:", r2)

        config_lay.addWidget(usage_box)

        # Notification methods
        notif_box = QGroupBox("Notification Methods")
        notif_lay = QVBoxLayout(notif_box)
        self.chk_sound  = QCheckBox("Sound alert (beep)")
        self.chk_toast  = QCheckBox("Windows system notification")
        self.chk_log    = QCheckBox("Log to database")
        self.chk_log.setChecked(True)
        notif_lay.addWidget(self.chk_sound)
        notif_lay.addWidget(self.chk_toast)
        notif_lay.addWidget(self.chk_log)
        config_lay.addWidget(notif_box)

        save_btn = QPushButton("💾  Save Configuration")
        save_btn.clicked.connect(self._save_config)
        config_lay.addWidget(save_btn)

        config_lay.addStretch()
        splitter.addWidget(config_w)

        # ── Right: history ──
        hist_w = QWidget()
        hist_lay = QVBoxLayout(hist_w)
        hist_lay.setContentsMargins(0, 0, 0, 0)
        hist_lay.setSpacing(8)

        hist_hdr = QHBoxLayout()
        hist_hdr.addWidget(QLabel("Alert History", objectName="SectionTitle"))
        hist_hdr.addStretch()
        clear_btn = QPushButton("🗑  Clear")
        clear_btn.setObjectName("BtnSecondary")
        clear_btn.clicked.connect(self._clear_history)
        hist_hdr.addWidget(clear_btn)
        hist_lay.addLayout(hist_hdr)

        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(4)
        self.hist_table.setHorizontalHeaderLabels(
            ["Time", "Type", "Message", "Severity"]
        )
        self.hist_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.hist_table.setAlternatingRowColors(True)
        self.hist_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.hist_table.verticalHeader().setVisible(False)
        hist_lay.addWidget(self.hist_table)

        splitter.addWidget(hist_w)
        splitter.setSizes([380, 620])
        root.addWidget(splitter)

    # ── slots ──────────────────────────────────────────────────────────────

    @pyqtSlot(str, str, str)
    def _on_alert(self, alert_type: str, message: str, severity: str):
        self._load_history()

    def _save_config(self):
        self.alert_mgr.configure(
            dl_limit_mb=self.dl_limit.value(),
            ul_limit_mb=self.ul_limit.value(),
            spike_factor=self.spike_factor.value(),
            sound=self.chk_sound.isChecked(),
            notify=self.chk_toast.isChecked(),
        )
        # Save to DB settings
        self.db.set_setting("alert_dl_limit", str(self.dl_limit.value()))
        self.db.set_setting("alert_ul_limit", str(self.ul_limit.value()))
        self.db.set_setting("alert_spike", str(self.spike_factor.value()))
        self.db.set_setting("alert_sound",
                             "1" if self.chk_sound.isChecked() else "0")
        self.db.set_setting("alert_toast",
                             "1" if self.chk_toast.isChecked() else "0")

        # Usage limits
        if self.daily_limit.value() > 0:
            self.db.set_limit("daily",
                               int(self.daily_limit.value() * 1_048_576),
                               self.daily_en.isChecked())
        if self.monthly_limit.value() > 0:
            self.db.set_limit("monthly",
                               int(self.monthly_limit.value() * 1_048_576),
                               self.monthly_en.isChecked())

    def _load_config(self):
        self.dl_limit.setValue(
            float(self.db.get_setting("alert_dl_limit", "0"))
        )
        self.ul_limit.setValue(
            float(self.db.get_setting("alert_ul_limit", "0"))
        )
        self.spike_factor.setValue(
            float(self.db.get_setting("alert_spike", "3.0"))
        )
        self.chk_sound.setChecked(
            self.db.get_setting("alert_sound", "1") == "1"
        )
        self.chk_toast.setChecked(
            self.db.get_setting("alert_toast", "1") == "1"
        )

    def _load_history(self):
        alerts = self.db.get_alerts(200)
        self.hist_table.setRowCount(len(alerts))
        sev_colors = {
            "critical": "#ef4444",
            "warning":  "#f59e0b",
            "info":     "#06b6d4",
        }
        for row, a in enumerate(alerts):
            ts = datetime.datetime.fromtimestamp(
                a["timestamp"]).strftime("%m-%d %H:%M:%S")
            sev = a["severity"]
            color = sev_colors.get(sev, "#94a3b8")
            for col, text in enumerate([
                ts, a["type"].replace("_", " ").title(),
                a["message"], sev.capitalize()
            ]):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 3:
                    item.setForeground(QColor(color))
                self.hist_table.setItem(row, col, item)

    def _clear_history(self):
        self.db.conn().execute("DELETE FROM alerts")
        self.db.conn().commit()
        self.hist_table.setRowCount(0)

    def apply_theme(self, dark: bool):
        self._dark = dark

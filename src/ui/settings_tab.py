"""
Settings tab: theme, interval, data retention, interface, startup.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QCheckBox, QFormLayout, QMessageBox,
    QLineEdit
)
from PyQt6.QtCore import pyqtSignal

from core.db_manager import DBManager
from core.network_monitor import NetworkMonitor


class SettingsTab(QWidget):
    theme_changed     = pyqtSignal(str)     # "dark" | "light"
    interval_changed  = pyqtSignal(float)
    interface_changed = pyqtSignal(str)

    def __init__(self, db: DBManager, monitor: NetworkMonitor, parent=None):
        super().__init__(parent)
        self.db = db
        self.monitor = monitor
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(20, 16, 20, 16)
        root.addWidget(QLabel("⚙  Settings", objectName="SectionTitle"))

        # ── Appearance ──
        app_box = QGroupBox("Appearance")
        app_form = QFormLayout(app_box)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        app_form.addRow("Theme:", self.theme_combo)
        root.addWidget(app_box)

        # ── Monitoring ──
        mon_box = QGroupBox("Monitoring")
        mon_form = QFormLayout(mon_box)

        self.iface_combo = QComboBox()
        self.iface_combo.addItems(NetworkMonitor.get_interfaces())
        mon_form.addRow("Network Interface:", self.iface_combo)

        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.5, 60.0)
        self.interval_spin.setSingleStep(0.5)
        self.interval_spin.setValue(1.0)
        self.interval_spin.setSuffix(" seconds")
        mon_form.addRow("Update Interval:", self.interval_spin)

        self.chk_start_minimized = QCheckBox("Start minimized to system tray")
        mon_form.addRow("", self.chk_start_minimized)

        self.chk_autostart = QCheckBox(
            "Run on Windows startup  (requires admin)"
        )
        mon_form.addRow("", self.chk_autostart)
        root.addWidget(mon_box)

        # ── Data / Storage ──
        data_box = QGroupBox("Data & Storage")
        data_form = QFormLayout(data_box)

        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(7, 3650)
        self.retention_spin.setValue(365)
        self.retention_spin.setSuffix(" days")
        data_form.addRow("Keep history for:", self.retention_spin)

        prune_btn = QPushButton("🗑  Prune Old Data Now")
        prune_btn.setObjectName("BtnSecondary")
        prune_btn.clicked.connect(self._prune)
        data_form.addRow("", prune_btn)

        self.db_path_lbl = QLabel()
        self.db_path_lbl.setObjectName("SubLabel")
        self.db_path_lbl.setWordWrap(True)
        data_form.addRow("Database:", self.db_path_lbl)
        root.addWidget(data_box)

        # ── Save ──
        save_btn = QPushButton("💾  Save Settings")
        save_btn.clicked.connect(self._save)
        root.addWidget(save_btn)

        root.addStretch()

    # ── persistence ────────────────────────────────────────────────────────

    def _load(self):
        theme = self.db.get_setting("theme", "dark")
        self.theme_combo.setCurrentText(theme.capitalize())

        iface = self.db.get_setting("interface", "All")
        idx = self.iface_combo.findText(iface)
        if idx >= 0:
            self.iface_combo.setCurrentIndex(idx)

        interval = float(self.db.get_setting("interval", "1.0"))
        self.interval_spin.setValue(interval)

        retention = int(self.db.get_setting("retention_days", "365"))
        self.retention_spin.setValue(retention)

        self.chk_start_minimized.setChecked(
            self.db.get_setting("start_minimized", "0") == "1"
        )
        self.db_path_lbl.setText(self.db.path)

    def _save(self):
        theme = self.theme_combo.currentText().lower()
        iface = self.iface_combo.currentText()
        interval = self.interval_spin.value()
        retention = self.retention_spin.value()

        self.db.set_setting("theme", theme)
        self.db.set_setting("interface", iface)
        self.db.set_setting("interval", str(interval))
        self.db.set_setting("retention_days", str(retention))
        self.db.set_setting(
            "start_minimized",
            "1" if self.chk_start_minimized.isChecked() else "0"
        )

        # Apply live
        self.theme_changed.emit(theme)
        self.monitor.set_interface(iface)
        self.monitor.set_interval(interval)

        QMessageBox.information(self, "Settings", "Settings saved successfully.")

    def _prune(self):
        days = self.retention_spin.value()
        self.db.prune_old_data(days)
        QMessageBox.information(
            self, "Prune Complete",
            f"Removed data older than {days} days."
        )

    def apply_theme(self, dark: bool):
        pass  # handled at app level

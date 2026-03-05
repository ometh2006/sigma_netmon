"""
System tray icon with live speed tooltip and context menu.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QSize

from core.network_monitor import NetworkMonitor


def _make_icon(dark: bool = True) -> QIcon:
    """Create a simple Σ icon programmatically."""
    size = 32
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background circle
    painter.setBrush(QColor("#7c3aed"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, size, size)

    # Σ text
    font = QFont("Segoe UI", 16, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "Σ")
    painter.end()
    return QIcon(px)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window, monitor: NetworkMonitor, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.monitor = monitor

        self.setIcon(_make_icon())
        self.setToolTip("Σ Dev Network Monitor — Starting …")

        self._build_menu()
        self.activated.connect(self._on_activated)
        monitor.stats_updated.connect(self._on_stats)

    def _build_menu(self):
        menu = QMenu()

        open_act = menu.addAction("📊  Open Dashboard")
        open_act.triggered.connect(self._show_window)

        menu.addSeparator()

        self.pause_act = menu.addAction("⏸  Pause Monitoring")
        self.pause_act.setCheckable(True)
        self.pause_act.triggered.connect(self._toggle_pause)

        menu.addSeparator()

        settings_act = menu.addAction("⚙  Settings")
        settings_act.triggered.connect(self._open_settings)

        menu.addSeparator()

        exit_act = menu.addAction("✖  Exit")
        exit_act.triggered.connect(self._exit)

        self.setContextMenu(menu)

    def _on_stats(self, stats: dict):
        dl = NetworkMonitor.format_speed(stats["dl_speed"])
        ul = NetworkMonitor.format_speed(stats["ul_speed"])
        self.setToolTip(
            f"Σ Dev Network Monitor\n"
            f"⬇ {dl}   ⬆ {ul}\n"
            f"Connections: {stats['conn_count']}"
        )

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _toggle_pause(self, checked: bool):
        if checked:
            self.monitor.stop()
            self.pause_act.setText("▶  Resume Monitoring")
        else:
            if not self.monitor.isRunning():
                self.monitor.start()
            self.pause_act.setText("⏸  Pause Monitoring")

    def _open_settings(self):
        self._show_window()
        # Navigate to settings tab
        if hasattr(self.main_window, "nav_to"):
            self.main_window.nav_to("Settings")

    def _exit(self):
        self.hide()
        self.monitor.stop()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

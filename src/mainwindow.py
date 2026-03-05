"""
MainWindow: sidebar nav, stacked pages, tray, DB write loop.
"""

import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QLabel, QStatusBar,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QCloseEvent

from core import NetworkMonitor, DBManager, AlertManager, ExportManager
from ui import (
    DashboardTab, StatisticsTab, ProcessesTab, ConnectionsTab,
    DiagnosticsTab, DevicesTab, AlertsTab, SettingsTab, TrayIcon
)
from styles import get_theme


_NAV_PAGES = [
    ("📊", "Dashboard",    "DashboardTab"),
    ("📈", "Statistics",   "StatisticsTab"),
    ("🔄", "Processes",    "ProcessesTab"),
    ("🔌", "Connections",  "ConnectionsTab"),
    ("🔧", "Diagnostics",  "DiagnosticsTab"),
    ("📡", "Devices",      "DevicesTab"),
    ("🔔", "Alerts",       "AlertsTab"),
    ("⚙",  "Settings",     "SettingsTab"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Σ Dev Network Monitor")
        self.setMinimumSize(1280, 800)

        # ── Core components ──
        self.db      = DBManager()
        self.monitor = NetworkMonitor()
        self.alert_mgr = AlertManager(db_manager=self.db)

        self._theme = self.db.get_setting("theme", "dark")
        self._tabs: dict[str, QWidget] = {}
        self._nav_btns: dict[str, QPushButton] = {}

        # ── Build UI ──
        self._build_ui()
        self._build_tray()
        self._apply_theme(self._theme)

        # ── DB write timer (every 60 s) ──
        self._db_timer = QTimer(self)
        self._db_timer.timeout.connect(self._write_db)
        self._db_timer.start(60_000)

        # ── Connect monitor ──
        self.monitor.stats_updated.connect(self._on_stats)
        self.monitor.stats_updated.connect(self.alert_mgr.evaluate)

        # ── Apply saved interface / interval ──
        iface    = self.db.get_setting("interface", "All")
        interval = float(self.db.get_setting("interval", "1.0"))
        self.monitor.set_interface(iface)
        self.monitor.set_interval(interval)
        self.monitor.start()

        # ── Load alert config ──
        self.alert_mgr.configure(
            dl_limit_mb=float(self.db.get_setting("alert_dl_limit", "0")),
            ul_limit_mb=float(self.db.get_setting("alert_ul_limit", "0")),
            spike_factor=float(self.db.get_setting("alert_spike", "3.0")),
            sound=self.db.get_setting("alert_sound", "1") == "1",
            notify=self.db.get_setting("alert_toast", "1") == "1",
        )

        # Minimise to tray if requested
        if self.db.get_setting("start_minimized", "0") == "1":
            QTimer.singleShot(0, self.hide)

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(0, 0, 0, 0)
        side_lay.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(60)
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(16, 0, 16, 0)
        logo_lbl = QLabel("Σ  NetMon")
        logo_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_lbl.setStyleSheet(
            "color: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #7c3aed,stop:1 #06b6d4);"
        )
        logo_lay.addWidget(logo_lbl)
        side_lay.addWidget(logo_frame)

        # Nav buttons
        side_lay.addSpacing(8)
        for icon, label, _ in _NAV_PAGES:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, lbl=label: self._nav_to(lbl))
            self._nav_btns[label] = btn
            side_lay.addWidget(btn)

        side_lay.addStretch()

        # Theme toggle at bottom
        self._theme_btn = QPushButton("☀  Light Mode")
        self._theme_btn.setObjectName("BtnSecondary")
        self._theme_btn.setFixedHeight(36)
        self._theme_btn.clicked.connect(self._toggle_theme)
        side_lay.addWidget(self._theme_btn)
        side_lay.addSpacing(12)

        root.addWidget(sidebar)

        # ── Main content ──
        content_frame = QFrame()
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar_lay = QHBoxLayout(topbar)
        topbar_lay.setContentsMargins(20, 0, 20, 0)

        self.page_title_lbl = QLabel("Dashboard")
        self.page_title_lbl.setObjectName("SectionTitle")
        self.page_title_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        topbar_lay.addWidget(self.page_title_lbl)
        topbar_lay.addStretch()

        self.speed_lbl = QLabel("⬇ — ⬆ —")
        self.speed_lbl.setObjectName("SubLabel")
        topbar_lay.addWidget(self.speed_lbl)
        content_lay.addWidget(topbar)

        # Stacked pages
        self.stack = QStackedWidget()

        # Instantiate all tabs
        self._tabs["Dashboard"]   = DashboardTab(self.monitor)
        self._tabs["Statistics"]  = StatisticsTab(self.db)
        self._tabs["Processes"]   = ProcessesTab()
        self._tabs["Connections"] = ConnectionsTab()
        self._tabs["Diagnostics"] = DiagnosticsTab()
        self._tabs["Devices"]     = DevicesTab(self.db)
        self._tabs["Alerts"]      = AlertsTab(self.db, self.alert_mgr)
        self._tabs["Settings"]    = SettingsTab(self.db, self.monitor)

        for _, label, _ in _NAV_PAGES:
            self.stack.addWidget(self._tabs[label])

        content_lay.addWidget(self.stack)
        root.addWidget(content_frame)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.sb_lbl = QLabel("Ready")
        sb.addPermanentWidget(self.sb_lbl)

        # Connect settings signals
        settings_tab: SettingsTab = self._tabs["Settings"]
        settings_tab.theme_changed.connect(self._apply_theme)
        settings_tab.interval_changed.connect(self.monitor.set_interval)
        settings_tab.interface_changed.connect(self.monitor.set_interface)

        # Select first nav
        self._nav_to("Dashboard")

    def _build_tray(self):
        self.tray = TrayIcon(self, self.monitor, self)
        self.tray.show()

    # ── navigation ─────────────────────────────────────────────────────────

    def _nav_to(self, label: str):
        for lbl, btn in self._nav_btns.items():
            btn.setChecked(lbl == label)

        idx = [n[1] for n in _NAV_PAGES].index(label)
        self.stack.setCurrentIndex(idx)
        self.page_title_lbl.setText(label)

    def nav_to(self, label: str):
        """Public accessor used by tray icon."""
        self._nav_to(label)

    # ── stats slot ─────────────────────────────────────────────────────────

    @pyqtSlot(dict)
    def _on_stats(self, stats: dict):
        dl = NetworkMonitor.format_speed(stats["dl_speed"])
        ul = NetworkMonitor.format_speed(stats["ul_speed"])
        self.speed_lbl.setText(
            f"⬇ <span style='color:#06b6d4'>{dl}</span>  "
            f"⬆ <span style='color:#f59e0b'>{ul}</span>  "
            f"🔗 {stats['conn_count']}"
        )
        self.speed_lbl.setTextFormat(Qt.TextFormat.RichText)

    # ── DB write ───────────────────────────────────────────────────────────

    def _write_db(self):
        """Write aggregated 60-second stats to SQLite."""
        # Use latest stats from monitor history
        h_dl = list(self.monitor.dl_history)
        h_ul = list(self.monitor.ul_history)
        if not h_dl:
            return
        import statistics as _s
        avg_dl = _s.mean(h_dl[-60:]) if h_dl else 0
        avg_ul = _s.mean(h_ul[-60:]) if h_ul else 0

        try:
            conns = len(__import__("psutil").net_connections(kind="all"))
        except Exception:
            conns = 0

        self.db.record_usage(
            ts=time.time(),
            interface=self.monitor.selected_interface,
            dl=int(avg_dl * 60),
            ul=int(avg_ul * 60),
            dl_speed=avg_dl,
            ul_speed=avg_ul,
            conns=conns,
        )

    # ── theme ──────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        new = "light" if self._theme == "dark" else "dark"
        self._apply_theme(new)

    def _apply_theme(self, name: str):
        self._theme = name
        self.setStyleSheet(get_theme(name))
        dark = name == "dark"
        label = "☀  Light Mode" if dark else "🌙  Dark Mode"
        self._theme_btn.setText(label)

        for tab in self._tabs.values():
            if hasattr(tab, "apply_theme"):
                tab.apply_theme(dark)

    # ── window events ──────────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent):
        # Minimise to tray instead of quitting
        event.ignore()
        self.hide()
        self.tray.showMessage(
            "Σ Dev Network Monitor",
            "App is still running in the system tray.",
            self.tray.MessageIcon.Information,
            2000,
        )

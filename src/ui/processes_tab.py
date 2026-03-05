"""
Processes tab: shows per-process network usage via psutil.
"""

import psutil
import time
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QFrame, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QColor

from core.network_monitor import NetworkMonitor


class ProcessesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._prev_net: dict = {}   # pid -> (bytes_sent, bytes_recv)
        self._prev_time: float = time.monotonic()
        self._dark = True
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)
        self._refresh()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("🔄  Per-Application Network Usage",
                              objectName="SectionTitle"))
        hdr.addStretch()

        refresh_btn = QPushButton("⟳  Refresh Now")
        refresh_btn.setObjectName("BtnSecondary")
        refresh_btn.clicked.connect(self._refresh)
        hdr.addWidget(refresh_btn)
        root.addLayout(hdr)

        note = QLabel(
            "ℹ  Requires administrator privileges for accurate per-process data on Windows."
        )
        note.setObjectName("SubLabel")
        note.setWordWrap(True)
        root.addWidget(note)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Process Name", "PID", "Download", "Upload",
            "Connections", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in range(1, 6):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        root.addWidget(self.table)

    # ── data ───────────────────────────────────────────────────────────────

    def _refresh(self):
        now = time.monotonic()
        elapsed = max(now - self._prev_time, 0.001)

        # Build a map: pid -> {name, conns, net}
        proc_data: dict[int, dict] = {}

        try:
            conns_by_pid: dict[int, int] = defaultdict(int)
            for c in psutil.net_connections(kind="all"):
                if c.pid:
                    conns_by_pid[c.pid] += 1
        except Exception:
            conns_by_pid = {}

        for proc in psutil.process_iter(
                ["pid", "name", "status", "connections"]):
            try:
                pid = proc.info["pid"]
                name = proc.info["name"] or "Unknown"
                status = proc.info["status"] or ""

                # Try to get per-process I/O (needs elevated perms on Windows)
                try:
                    net = proc.net_io_counters()
                    prev = self._prev_net.get(pid)
                    if prev and net:
                        dl = max(0, net.bytes_recv - prev[1]) / elapsed
                        ul = max(0, net.bytes_sent - prev[0]) / elapsed
                    else:
                        dl = ul = 0.0
                    if net:
                        self._prev_net[pid] = (net.bytes_sent, net.bytes_recv)
                except Exception:
                    dl = ul = 0.0

                conn_count = conns_by_pid.get(pid, 0)

                if conn_count > 0 or dl > 0 or ul > 0:
                    proc_data[pid] = {
                        "name": name,
                        "status": status,
                        "dl": dl,
                        "ul": ul,
                        "conns": conn_count,
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self._prev_time = now

        # Sort by download speed desc
        sorted_procs = sorted(proc_data.items(),
                              key=lambda x: x[1]["dl"] + x[1]["ul"],
                              reverse=True)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(sorted_procs))

        for row, (pid, info) in enumerate(sorted_procs):
            items = [
                self._item(info["name"]),
                self._item(str(pid), align=Qt.AlignmentFlag.AlignCenter),
                self._item(NetworkMonitor.format_speed(info["dl"]),
                           color="#06b6d4"),
                self._item(NetworkMonitor.format_speed(info["ul"]),
                           color="#f59e0b"),
                self._item(str(info["conns"]),
                           align=Qt.AlignmentFlag.AlignCenter),
                self._item(info["status"].capitalize()),
            ]
            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)

    @staticmethod
    def _item(text: str,
              align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
              color: str | None = None) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        if color:
            item.setForeground(QColor(color))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def apply_theme(self, dark: bool):
        self._dark = dark

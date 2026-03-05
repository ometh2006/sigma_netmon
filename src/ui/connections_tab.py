"""
Connections tab: live view of all active network connections.
"""

import psutil
import socket
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QLineEdit, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor


# Background thread for DNS reverse lookup (so UI stays responsive)
class ResolveThread(QThread):
    resolved = pyqtSignal(str, str)  # ip -> hostname

    def __init__(self, ip: str, parent=None):
        super().__init__(parent)
        self.ip = ip

    def run(self):
        try:
            host = socket.gethostbyaddr(self.ip)[0]
        except Exception:
            host = self.ip
        self.resolved.emit(self.ip, host)


class ConnectionsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = True
        self._dns_cache: dict[str, str] = {}
        self._resolve_threads: list[ResolveThread] = []
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)
        self._refresh()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("🔌  Active Network Connections",
                              objectName="SectionTitle"))
        hdr.addStretch()

        self.count_lbl = QLabel("0 connections")
        self.count_lbl.setObjectName("SubLabel")
        hdr.addWidget(self.count_lbl)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setObjectName("BtnSecondary")
        refresh_btn.clicked.connect(self._refresh)
        hdr.addWidget(refresh_btn)
        root.addLayout(hdr)

        # ── Filter row ──
        flt = QHBoxLayout()
        flt.addWidget(QLabel("Filter:", objectName="SubLabel"))

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search IP / process …")
        self.search.textChanged.connect(self._apply_filter)
        flt.addWidget(self.search)

        flt.addWidget(QLabel("Protocol:", objectName="SubLabel"))
        self.proto_combo = QComboBox()
        self.proto_combo.addItems(["All", "TCP", "UDP"])
        self.proto_combo.currentIndexChanged.connect(self._apply_filter)
        flt.addWidget(self.proto_combo)

        flt.addWidget(QLabel("State:", objectName="SubLabel"))
        self.state_combo = QComboBox()
        self.state_combo.addItems(["All", "ESTABLISHED", "LISTEN",
                                    "TIME_WAIT", "CLOSE_WAIT", "SYN_SENT"])
        self.state_combo.currentIndexChanged.connect(self._apply_filter)
        flt.addWidget(self.state_combo)
        root.addLayout(flt)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Process", "PID", "Protocol",
            "Local Address", "Remote Address", "Remote Host",
            "Port", "State"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        root.addWidget(self.table)

        self._all_rows: list[dict] = []

    # ── data ───────────────────────────────────────────────────────────────

    def _refresh(self):
        pid_name: dict[int, str] = {}
        try:
            for p in psutil.process_iter(["pid", "name"]):
                pid_name[p.info["pid"]] = p.info["name"] or "Unknown"
        except Exception:
            pass

        rows = []
        try:
            for c in psutil.net_connections(kind="all"):
                proto = "TCP" if c.type == 1 else "UDP"
                la = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "—"
                ra = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "—"
                rem_ip = c.raddr.ip if c.raddr else ""
                rem_port = str(c.raddr.port) if c.raddr else "—"
                state = c.status or "—"
                proc = pid_name.get(c.pid, "Unknown") if c.pid else "System"
                pid = str(c.pid) if c.pid else "—"

                # Async DNS
                host = self._dns_cache.get(rem_ip, rem_ip)

                rows.append({
                    "proc": proc, "pid": pid, "proto": proto,
                    "la": la, "ra": ra, "host": host,
                    "port": rem_port, "state": state,
                    "rem_ip": rem_ip,
                })
        except Exception:
            pass

        self._all_rows = rows
        # Kick off DNS for new IPs
        for r in rows:
            ip = r["rem_ip"]
            if ip and ip not in self._dns_cache:
                self._dns_cache[ip] = ip  # placeholder
                t = ResolveThread(ip, self)
                t.resolved.connect(self._on_resolved)
                t.start()
                self._resolve_threads.append(t)

        self._apply_filter()

    def _apply_filter(self):
        search = self.search.text().lower()
        proto_f = self.proto_combo.currentText()
        state_f = self.state_combo.currentText()

        filtered = [
            r for r in self._all_rows
            if (not search or search in r["proc"].lower()
                or search in r["ra"] or search in r["la"]
                or search in r["host"].lower())
            and (proto_f == "All" or r["proto"] == proto_f)
            and (state_f == "All" or r["state"] == state_f)
        ]

        self.count_lbl.setText(f"{len(filtered)} connections")
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered))

        state_colors = {
            "ESTABLISHED": "#10b981",
            "LISTEN":      "#06b6d4",
            "TIME_WAIT":   "#f59e0b",
            "CLOSE_WAIT":  "#ef4444",
        }

        for row, r in enumerate(filtered):
            sc = state_colors.get(r["state"], "#94a3b8")
            cells = [
                (r["proc"], None),
                (r["pid"],  Qt.AlignmentFlag.AlignCenter),
                (r["proto"], Qt.AlignmentFlag.AlignCenter),
                (r["la"],   None),
                (r["ra"],   None),
                (r["host"], None),
                (r["port"], Qt.AlignmentFlag.AlignCenter),
                (r["state"], Qt.AlignmentFlag.AlignCenter),
            ]
            for col, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                if align:
                    item.setTextAlignment(align)
                if col == 7:  # state column coloring
                    item.setForeground(QColor(sc))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)

    def _on_resolved(self, ip: str, hostname: str):
        self._dns_cache[ip] = hostname

    def apply_theme(self, dark: bool):
        self._dark = dark

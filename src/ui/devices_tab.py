"""
Devices tab: ARP scan to discover LAN devices.
"""

import subprocess
import re
import socket
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

from core.db_manager import DBManager


# Known OUI vendor prefixes (subset)
_VENDORS: dict[str, str] = {
    "00:50:56": "VMware",      "00:0c:29": "VMware",
    "00:1a:11": "Google",      "b8:27:eb": "Raspberry Pi",
    "dc:a6:32": "Raspberry Pi","3c:22:fb": "Apple",
    "a4:83:e7": "Apple",       "00:1b:21": "Intel",
    "28:d2:44": "Microsoft",   "00:15:5d": "Microsoft Hyper-V",
    "9c:b6:d0": "Samsung",     "00:26:b9": "Dell",
    "f8:bc:12": "Cisco",
}


def _lookup_vendor(mac: str) -> str:
    prefix = mac[:8].upper()
    for k, v in _VENDORS.items():
        if k.upper() == prefix:
            return v
    return "Unknown"


class ARPScanner(QThread):
    device_found = pyqtSignal(dict)   # {ip, mac, vendor, hostname}
    finished     = pyqtSignal(int)    # total count

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        devices = {}
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in result.stdout.splitlines():
                m = re.search(
                    r"(\d+\.\d+\.\d+\.\d+)\s+([\da-f]{2}[:\-][\da-f]{2}[:\-]"
                    r"[\da-f]{2}[:\-][\da-f]{2}[:\-][\da-f]{2}[:\-][\da-f]{2})",
                    line, re.IGNORECASE
                )
                if m:
                    ip = m.group(1)
                    mac = m.group(2).replace("-", ":").lower()
                    if ip.startswith("224.") or ip.startswith("239."):
                        continue  # skip multicast
                    if mac == "ff:ff:ff:ff:ff:ff":
                        continue  # skip broadcast
                    devices[ip] = mac

        except Exception:
            pass

        count = 0
        for ip, mac in devices.items():
            vendor = _lookup_vendor(mac)
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = ""
            self.device_found.emit({
                "ip": ip, "mac": mac,
                "vendor": vendor, "hostname": hostname
            })
            count += 1

        self.finished.emit(count)


class DevicesTab(QWidget):
    def __init__(self, db: DBManager, parent=None):
        super().__init__(parent)
        self.db = db
        self._dark = True
        self._scanner: ARPScanner | None = None
        self._setup_ui()
        self._load_from_db()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("📡  Network Devices", objectName="SectionTitle"))
        hdr.addStretch()

        self.count_lbl = QLabel("0 devices")
        self.count_lbl.setObjectName("SubLabel")
        hdr.addWidget(self.count_lbl)

        self.scan_btn = QPushButton("🔍  Scan Network")
        self.scan_btn.clicked.connect(self._start_scan)
        hdr.addWidget(self.scan_btn)
        root.addLayout(hdr)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)  # indeterminate
        root.addWidget(self.progress)

        note = QLabel(
            "ℹ  Devices discovered via ARP table. Run Scan to refresh. "
            "Results are also saved to the local database."
        )
        note.setObjectName("SubLabel")
        note.setWordWrap(True)
        root.addWidget(note)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "IP Address", "MAC Address", "Vendor", "Hostname", "Last Seen"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        root.addWidget(self.table)

    # ── scan ───────────────────────────────────────────────────────────────

    def _start_scan(self):
        if self._scanner and self._scanner.isRunning():
            return
        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.table.setRowCount(0)

        self._scanner = ARPScanner(self)
        self._scanner.device_found.connect(self._on_device)
        self._scanner.finished.connect(self._on_scan_done)
        self._scanner.start()

    def _on_device(self, dev: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._set_row(row, dev["ip"], dev["mac"], dev["vendor"],
                      dev["hostname"], "just now")
        self.count_lbl.setText(f"{row + 1} devices")
        self.db.upsert_device(dev["ip"], dev["mac"],
                              dev["vendor"], dev["hostname"])

    def _on_scan_done(self, count: int):
        self.scan_btn.setEnabled(True)
        self.progress.setVisible(False)
        self.count_lbl.setText(f"{count} devices found")

    def _load_from_db(self):
        rows = self.db.get_devices()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            import datetime
            ts = datetime.datetime.fromtimestamp(
                r["last_seen"]).strftime("%Y-%m-%d %H:%M") if r["last_seen"] else "—"
            self._set_row(i, r["ip"] or "—", r["mac"] or "—",
                          r["vendor"] or "Unknown",
                          r["hostname"] or "—", ts)
        self.count_lbl.setText(f"{len(rows)} devices")

    def _set_row(self, row: int, ip: str, mac: str,
                 vendor: str, hostname: str, ts: str):
        for col, text in enumerate([ip, mac, vendor, hostname, ts]):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if col == 0:
                item.setForeground(QColor("#06b6d4"))
            self.table.setItem(row, col, item)

    def apply_theme(self, dark: bool):
        self._dark = dark

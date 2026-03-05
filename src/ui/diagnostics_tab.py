"""
Diagnostics tab: ping monitor, traceroute, DNS lookup.
"""

import subprocess
import re
import socket
import time
from collections import deque

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np


# ── Worker threads ──────────────────────────────────────────────────────────

class PingWorker(QThread):
    result = pyqtSignal(float, float)   # latency_ms, packet_loss (0–100)
    error  = pyqtSignal(str)

    def __init__(self, host: str, parent=None):
        super().__init__(parent)
        self.host = host
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                t0 = time.monotonic()
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "2000", self.host],
                    capture_output=True, text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                elapsed = (time.monotonic() - t0) * 1000

                out = result.stdout
                m = re.search(r"time[=<](\d+)ms", out, re.IGNORECASE)
                loss_m = re.search(r"\((\d+)% loss\)", out)

                latency = float(m.group(1)) if m else -1.0
                loss = float(loss_m.group(1)) if loss_m else (0.0 if latency >= 0 else 100.0)
                self.result.emit(latency, loss)
            except Exception as e:
                self.error.emit(str(e))
            time.sleep(1)

    def stop(self):
        self.running = False


class TracerouteWorker(QThread):
    output_line = pyqtSignal(str)
    finished    = pyqtSignal()

    def __init__(self, host: str, parent=None):
        super().__init__(parent)
        self.host = host

    def run(self):
        try:
            proc = subprocess.Popen(
                ["tracert", "-d", "-w", "2000", self.host],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in proc.stdout:
                self.output_line.emit(line.rstrip())
            proc.wait()
        except Exception as e:
            self.output_line.emit(f"Error: {e}")
        self.finished.emit()


# ── Tab widget ───────────────────────────────────────────────────────────────

class DiagnosticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = True
        self._ping_history: deque[float] = deque([0.0] * 60, maxlen=60)
        self._loss_history: deque[float] = deque([0.0] * 60, maxlen=60)
        self._ping_worker: PingWorker | None = None
        self._tracer_worker: TracerouteWorker | None = None
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        root.addWidget(QLabel("🔧  Network Diagnostics",
                               objectName="SectionTitle"))

        tabs = QTabWidget()
        tabs.addTab(self._build_ping_tab(), "🏓  Ping Monitor")
        tabs.addTab(self._build_trace_tab(), "🗺  Traceroute")
        tabs.addTab(self._build_dns_tab(), "🔎  DNS Lookup")
        root.addWidget(tabs)

    # ── Ping ──

    def _build_ping_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.setContentsMargins(12, 12, 12, 12)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Host / IP:", objectName="SubLabel"))
        self.ping_host = QLineEdit("8.8.8.8")
        ctrl.addWidget(self.ping_host)
        self.ping_btn = QPushButton("▶  Start")
        self.ping_btn.clicked.connect(self._toggle_ping)
        ctrl.addWidget(self.ping_btn)
        lay.addLayout(ctrl)

        # Stat row
        stat_row = QHBoxLayout()
        self.lbl_latency  = self._stat_lbl("Latency",     "#06b6d4")
        self.lbl_loss     = self._stat_lbl("Packet Loss", "#ef4444")
        self.lbl_jitter   = self._stat_lbl("Jitter",      "#f59e0b")
        for w2 in (self.lbl_latency, self.lbl_loss, self.lbl_jitter):
            stat_row.addWidget(w2)
        lay.addLayout(stat_row)

        # Chart
        self.ping_plot = pg.PlotWidget()
        self.ping_plot.setBackground("#0f1629")
        self.ping_plot.showGrid(x=False, y=True, alpha=0.15)
        self.ping_plot.setLabel("left", "ms")
        self.ping_plot.setMinimumHeight(200)
        self.ping_plot.setXRange(0, 60, padding=0)
        lay.addWidget(self.ping_plot)

        self._ping_curve = self.ping_plot.plot(
            pen=pg.mkPen("#06b6d4", width=2), fillLevel=0,
            brush=pg.mkBrush(6, 182, 212, 40)
        )
        return w

    def _stat_lbl(self, title: str, color: str) -> QFrame:
        f = QFrame()
        f.setObjectName("Card")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(14, 10, 14, 10)
        t = QLabel(title.upper())
        t.setObjectName("StatLabel")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v = QLabel("—")
        v.setObjectName("StatValue")
        v.setStyleSheet(f"color: {color}; font-size: 20px;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        lay.addWidget(v)
        f._val_lbl = v
        return f

    def _toggle_ping(self):
        if self._ping_worker and self._ping_worker.isRunning():
            self._ping_worker.stop()
            self._ping_worker.wait()
            self._ping_worker = None
            self.ping_btn.setText("▶  Start")
        else:
            host = self.ping_host.text().strip() or "8.8.8.8"
            self._ping_worker = PingWorker(host, self)
            self._ping_worker.result.connect(self._on_ping)
            self._ping_worker.error.connect(
                lambda e: self.lbl_latency._val_lbl.setText("ERR")
            )
            self._ping_worker.start()
            self.ping_btn.setText("⏹  Stop")

    def _on_ping(self, latency: float, loss: float):
        self._ping_history.append(max(0, latency))
        self._loss_history.append(loss)

        arr = np.array(list(self._ping_history))
        self._ping_curve.setData(np.arange(len(arr)), arr)

        valid = arr[arr > 0]
        jitter = float(np.std(valid)) if len(valid) > 1 else 0.0

        lat_txt = f"{latency:.0f} ms" if latency >= 0 else "Timeout"
        self.lbl_latency._val_lbl.setText(lat_txt)
        self.lbl_loss._val_lbl.setText(f"{loss:.0f}%")
        self.lbl_jitter._val_lbl.setText(f"{jitter:.1f} ms")

    # ── Traceroute ──

    def _build_trace_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.setContentsMargins(12, 12, 12, 12)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Target:", objectName="SubLabel"))
        self.trace_host = QLineEdit("google.com")
        ctrl.addWidget(self.trace_host)
        self.trace_btn = QPushButton("▶  Run Traceroute")
        self.trace_btn.clicked.connect(self._run_trace)
        ctrl.addWidget(self.trace_btn)
        lay.addLayout(ctrl)

        self.trace_output = QTextEdit()
        self.trace_output.setReadOnly(True)
        self.trace_output.setPlaceholderText(
            "Traceroute results will appear here …"
        )
        lay.addWidget(self.trace_output)
        return w

    def _run_trace(self):
        host = self.trace_host.text().strip() or "google.com"
        self.trace_output.clear()
        self.trace_output.append(f"Tracing route to {host} …\n")
        self.trace_btn.setEnabled(False)

        if self._tracer_worker and self._tracer_worker.isRunning():
            return

        self._tracer_worker = TracerouteWorker(host, self)
        self._tracer_worker.output_line.connect(
            lambda l: self.trace_output.append(l)
        )
        self._tracer_worker.finished.connect(
            lambda: self.trace_btn.setEnabled(True)
        )
        self._tracer_worker.start()

    # ── DNS ──

    def _build_dns_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.setContentsMargins(12, 12, 12, 12)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Domain / IP:", objectName="SubLabel"))
        self.dns_input = QLineEdit("google.com")
        ctrl.addWidget(self.dns_input)
        lookup_btn = QPushButton("🔎  Lookup")
        lookup_btn.clicked.connect(self._dns_lookup)
        ctrl.addWidget(lookup_btn)
        lay.addLayout(ctrl)

        self.dns_output = QTextEdit()
        self.dns_output.setReadOnly(True)
        self.dns_output.setPlaceholderText("DNS results will appear here …")
        lay.addWidget(self.dns_output)
        return w

    def _dns_lookup(self):
        host = self.dns_input.text().strip()
        if not host:
            return
        self.dns_output.clear()
        try:
            # Forward lookup
            t0 = time.perf_counter()
            infos = socket.getaddrinfo(host, None)
            elapsed = (time.perf_counter() - t0) * 1000

            ips = list(dict.fromkeys(i[4][0] for i in infos))
            self.dns_output.append(f"=== DNS Lookup: {host} ===")
            self.dns_output.append(f"Resolved in {elapsed:.1f} ms\n")
            for ip in ips:
                af = "IPv6" if ":" in ip else "IPv4"
                self.dns_output.append(f"  {af}  →  {ip}")

            # Reverse lookup for first IP
            self.dns_output.append("")
            try:
                rev = socket.gethostbyaddr(ips[0])[0]
                self.dns_output.append(f"Reverse: {ips[0]} → {rev}")
            except Exception:
                self.dns_output.append(f"Reverse: (no PTR record)")
        except Exception as e:
            self.dns_output.append(f"Error: {e}")

    # ── cleanup ────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._ping_worker:
            self._ping_worker.stop()
        super().closeEvent(event)

    def apply_theme(self, dark: bool):
        self._dark = dark
        bg = "#0f1629" if dark else "#ffffff"
        self.ping_plot.setBackground(bg)

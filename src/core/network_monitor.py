"""
Network monitor — collects real-time stats via psutil.
Emits a stats dict every `interval` seconds via Qt signal.
"""

import time
import socket
import psutil
from collections import deque

from PyQt6.QtCore import QThread, pyqtSignal


MAX_HISTORY = 120  # 2 minutes of 1-second samples


class NetworkMonitor(QThread):
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.interval = 1.0
        self.running = False
        self.selected_interface = "All"

        # Rolling history for charts
        self.dl_history: deque[float] = deque([0.0] * MAX_HISTORY, maxlen=MAX_HISTORY)
        self.ul_history: deque[float] = deque([0.0] * MAX_HISTORY, maxlen=MAX_HISTORY)

        self._prev_counters: dict = {}
        self._prev_time: float = 0.0

    # ── public API ─────────────────────────────────────────────────────────

    def set_interface(self, iface: str):
        self.selected_interface = iface

    def set_interval(self, seconds: float):
        self.interval = max(0.5, seconds)

    def stop(self):
        self.running = False

    # ── thread ─────────────────────────────────────────────────────────────

    def run(self):
        self.running = True
        # Seed baseline
        self._prev_counters = psutil.net_io_counters(pernic=True)
        self._prev_time = time.monotonic()

        while self.running:
            time.sleep(self.interval)
            stats = self._collect()
            self.stats_updated.emit(stats)

    # ── internals ──────────────────────────────────────────────────────────

    def _collect(self) -> dict:
        now = time.monotonic()
        elapsed = now - self._prev_time
        if elapsed <= 0:
            elapsed = self.interval

        curr_counters = psutil.net_io_counters(pernic=True)

        dl_bytes = 0
        ul_bytes = 0
        dl_total = 0
        ul_total = 0
        packets_recv = 0
        packets_sent = 0

        if self.selected_interface == "All":
            for name, c in curr_counters.items():
                p = self._prev_counters.get(name)
                if p:
                    dl_bytes += max(0, c.bytes_recv - p.bytes_recv)
                    ul_bytes += max(0, c.bytes_sent - p.bytes_sent)
                    packets_recv += max(0, c.packets_recv - p.packets_recv)
                    packets_sent += max(0, c.packets_sent - p.packets_sent)
                dl_total += c.bytes_recv
                ul_total += c.bytes_sent
        else:
            c = curr_counters.get(self.selected_interface)
            p = self._prev_counters.get(self.selected_interface)
            if c and p:
                dl_bytes = max(0, c.bytes_recv - p.bytes_recv)
                ul_bytes = max(0, c.bytes_sent - p.bytes_sent)
                packets_recv = max(0, c.packets_recv - p.packets_recv)
                packets_sent = max(0, c.packets_sent - p.packets_sent)
            if c:
                dl_total = c.bytes_recv
                ul_total = c.bytes_sent

        dl_speed = dl_bytes / elapsed  # bytes/sec
        ul_speed = ul_bytes / elapsed

        self.dl_history.append(dl_speed)
        self.ul_history.append(ul_speed)
        self._prev_counters = curr_counters
        self._prev_time = now

        # Connection count
        try:
            connections = psutil.net_connections(kind='all')
            conn_count = len(connections)
        except Exception:
            conn_count = 0

        return {
            "dl_speed": dl_speed,
            "ul_speed": ul_speed,
            "dl_total": dl_total,
            "ul_total": ul_total,
            "packets_recv_ps": packets_recv / elapsed,
            "packets_sent_ps": packets_sent / elapsed,
            "conn_count": conn_count,
            "dl_history": list(self.dl_history),
            "ul_history": list(self.ul_history),
            "interfaces": list(curr_counters.keys()),
            "timestamp": time.time(),
        }

    # ── utilities ──────────────────────────────────────────────────────────

    @staticmethod
    def get_interfaces() -> list[str]:
        return ["All"] + list(psutil.net_io_counters(pernic=True).keys())

    @staticmethod
    def format_speed(bps: float) -> str:
        if bps >= 1_000_000_000:
            return f"{bps/1_000_000_000:.2f} GB/s"
        if bps >= 1_000_000:
            return f"{bps/1_000_000:.2f} MB/s"
        if bps >= 1_000:
            return f"{bps/1_000:.1f} KB/s"
        return f"{bps:.0f} B/s"

    @staticmethod
    def format_bytes(b: int) -> str:
        if b >= 1_073_741_824:
            return f"{b/1_073_741_824:.2f} GB"
        if b >= 1_048_576:
            return f"{b/1_048_576:.2f} MB"
        if b >= 1_024:
            return f"{b/1_024:.1f} KB"
        return f"{b} B"

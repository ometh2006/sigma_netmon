"""
Alert manager: evaluates conditions and fires Windows toast / sound alerts.
"""

import time
import winsound
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from winotify import Notification, audio as wn_audio  # optional
    _HAS_WINOTIFY = True
except ImportError:
    _HAS_WINOTIFY = False


class AlertManager(QObject):
    alert_fired = pyqtSignal(str, str, str)  # type, message, severity

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager

        # Thresholds (configurable)
        self.dl_limit_bps: float = 0          # 0 = disabled
        self.ul_limit_bps: float = 0
        self.spike_factor: float = 3.0        # × avg to call "spike"
        self.sound_enabled: bool = True
        self.notify_enabled: bool = True

        self._avg_dl: float = 0.0
        self._avg_ul: float = 0.0
        self._sample_count: int = 0
        self._last_offline_alert: float = 0.0
        self._prev_conn_count: int = -1

    # ── public API ─────────────────────────────────────────────────────────

    def configure(self, dl_limit_mb: float, ul_limit_mb: float,
                  spike_factor: float, sound: bool, notify: bool):
        self.dl_limit_bps = dl_limit_mb * 1_000_000 if dl_limit_mb > 0 else 0
        self.ul_limit_bps = ul_limit_mb * 1_000_000 if ul_limit_mb > 0 else 0
        self.spike_factor = spike_factor
        self.sound_enabled = sound
        self.notify_enabled = notify

    def evaluate(self, stats: dict):
        """Called every stats update cycle."""
        dl = stats.get("dl_speed", 0.0)
        ul = stats.get("ul_speed", 0.0)
        conns = stats.get("conn_count", 0)

        # Rolling average (exponential moving)
        α = 0.05
        if self._sample_count == 0:
            self._avg_dl = dl
            self._avg_ul = ul
        else:
            self._avg_dl = α * dl + (1 - α) * self._avg_dl
            self._avg_ul = α * ul + (1 - α) * self._avg_ul
        self._sample_count += 1

        # Bandwidth limit exceeded
        if self.dl_limit_bps > 0 and dl > self.dl_limit_bps:
            self._fire("bandwidth_limit",
                       f"Download speed {dl/1e6:.1f} MB/s exceeded limit "
                       f"{self.dl_limit_bps/1e6:.1f} MB/s",
                       "warning")

        if self.ul_limit_bps > 0 and ul > self.ul_limit_bps:
            self._fire("bandwidth_limit",
                       f"Upload speed {ul/1e6:.1f} MB/s exceeded limit "
                       f"{self.ul_limit_bps/1e6:.1f} MB/s",
                       "warning")

        # Spike detection (only after warm-up)
        if self._sample_count > 30 and self._avg_dl > 10_000:
            if dl > self.spike_factor * self._avg_dl:
                self._fire("traffic_spike",
                           f"Unusual download spike: {dl/1e6:.2f} MB/s "
                           f"({self.spike_factor:.0f}× average)",
                           "warning")

        # Connection drop detection
        if self._prev_conn_count > 5 and conns == 0:
            now = time.time()
            if now - self._last_offline_alert > 60:
                self._fire("connection_lost",
                           "Network connection appears to be lost (0 active connections)",
                           "critical")
                self._last_offline_alert = now
        self._prev_conn_count = conns

    # ── internals ──────────────────────────────────────────────────────────

    _cooldown: dict[str, float] = {}  # per-type last-fire time
    _COOLDOWN_SEC = 30

    def _fire(self, alert_type: str, message: str, severity: str):
        now = time.time()
        last = self._cooldown.get(alert_type, 0)
        if now - last < self._COOLDOWN_SEC:
            return
        self._cooldown[alert_type] = now

        self.alert_fired.emit(alert_type, message, severity)
        if self.db:
            self.db.log_alert(alert_type, message, severity)
        if self.sound_enabled:
            self._beep(severity)
        if self.notify_enabled:
            self._toast(message, severity)

    @staticmethod
    def _beep(severity: str):
        try:
            freq = {"critical": 1200, "warning": 900, "info": 600}.get(severity, 600)
            winsound.Beep(freq, 200)
        except Exception:
            pass

    @staticmethod
    def _toast(message: str, severity: str):
        if _HAS_WINOTIFY:
            try:
                toast = Notification(
                    app_id="Σ Dev Network Monitor",
                    title=f"Network Alert – {severity.capitalize()}",
                    msg=message,
                    duration="short",
                )
                toast.show()
            except Exception:
                pass

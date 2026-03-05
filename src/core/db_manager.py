"""
SQLite-backed persistence for bandwidth history, app usage, alerts, and devices.
"""

import sqlite3
import os
import time
import json
from pathlib import Path


def _db_path() -> str:
    data = Path(os.environ.get("APPDATA", Path.home())) / "SigmaNetMon"
    data.mkdir(parents=True, exist_ok=True)
    return str(data / "netmon.db")


class DBManager:
    def __init__(self, path: str | None = None):
        self.path = path or _db_path()
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    # ── connection ─────────────────────────────────────────────────────────

    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self):
        c = self.conn()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS network_usage (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL    NOT NULL,
                interface TEXT    NOT NULL DEFAULT 'All',
                dl_bytes  INTEGER NOT NULL DEFAULT 0,
                ul_bytes  INTEGER NOT NULL DEFAULT 0,
                dl_speed  REAL    NOT NULL DEFAULT 0,
                ul_speed  REAL    NOT NULL DEFAULT 0,
                conn_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_nu_ts ON network_usage(timestamp);

            CREATE TABLE IF NOT EXISTS application_usage (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL    NOT NULL,
                pid       INTEGER NOT NULL,
                name      TEXT    NOT NULL,
                dl_bytes  INTEGER NOT NULL DEFAULT 0,
                ul_bytes  INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_au_ts ON application_usage(timestamp);

            CREATE TABLE IF NOT EXISTS connection_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  REAL    NOT NULL,
                pid        INTEGER,
                proc_name  TEXT,
                local_addr TEXT,
                remote_addr TEXT,
                protocol   TEXT,
                status     TEXT
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL    NOT NULL,
                type      TEXT    NOT NULL,
                message   TEXT    NOT NULL,
                severity  TEXT    NOT NULL DEFAULT 'info'
            );

            CREATE TABLE IF NOT EXISTS devices (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ip         TEXT    NOT NULL,
                mac        TEXT,
                vendor     TEXT,
                hostname   TEXT,
                first_seen REAL,
                last_seen  REAL,
                UNIQUE(mac)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS usage_limits (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                period       TEXT    NOT NULL,
                limit_bytes  INTEGER NOT NULL,
                enabled      INTEGER NOT NULL DEFAULT 1
            );
        """)
        c.commit()

    # ── network usage ──────────────────────────────────────────────────────

    def record_usage(self, ts: float, interface: str, dl: int, ul: int,
                     dl_speed: float, ul_speed: float, conns: int):
        self.conn().execute(
            "INSERT INTO network_usage(timestamp,interface,dl_bytes,ul_bytes,"
            "dl_speed,ul_speed,conn_count) VALUES(?,?,?,?,?,?,?)",
            (ts, interface, dl, ul, dl_speed, ul_speed, conns)
        )
        self.conn().commit()

    def get_usage_range(self, start: float, end: float,
                        interface: str = "All") -> list[sqlite3.Row]:
        q = ("SELECT * FROM network_usage WHERE timestamp BETWEEN ? AND ? "
             "AND interface=? ORDER BY timestamp")
        return self.conn().execute(q, (start, end, interface)).fetchall()

    def get_aggregated_usage(self, period: str) -> dict:
        """Return total DL/UL for today/week/month/year/alltime."""
        now = time.time()
        if period == "today":
            import datetime
            midnight = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0).timestamp()
            start = midnight
        elif period == "week":
            start = now - 7 * 86400
        elif period == "month":
            start = now - 30 * 86400
        elif period == "year":
            start = now - 365 * 86400
        else:
            start = 0

        row = self.conn().execute(
            "SELECT SUM(dl_bytes) as dl, SUM(ul_bytes) as ul, "
            "MAX(dl_speed) as peak_dl, MAX(ul_speed) as peak_ul, "
            "AVG(dl_speed) as avg_dl, AVG(ul_speed) as avg_ul "
            "FROM network_usage WHERE timestamp>=?", (start,)
        ).fetchone()
        return {
            "dl": row["dl"] or 0,
            "ul": row["ul"] or 0,
            "peak_dl": row["peak_dl"] or 0,
            "peak_ul": row["peak_ul"] or 0,
            "avg_dl": row["avg_dl"] or 0,
            "avg_ul": row["avg_ul"] or 0,
        }

    def get_daily_usage(self, days: int = 30) -> list[dict]:
        """Returns list of {date, dl, ul} dicts for charting."""
        start = time.time() - days * 86400
        rows = self.conn().execute(
            "SELECT date(timestamp,'unixepoch','localtime') as d, "
            "SUM(dl_bytes) as dl, SUM(ul_bytes) as ul "
            "FROM network_usage WHERE timestamp>=? GROUP BY d ORDER BY d",
            (start,)
        ).fetchall()
        return [{"date": r["d"], "dl": r["dl"] or 0, "ul": r["ul"] or 0}
                for r in rows]

    # ── alerts ─────────────────────────────────────────────────────────────

    def log_alert(self, alert_type: str, message: str, severity: str = "info"):
        self.conn().execute(
            "INSERT INTO alerts(timestamp,type,message,severity) VALUES(?,?,?,?)",
            (time.time(), alert_type, message, severity)
        )
        self.conn().commit()

    def get_alerts(self, limit: int = 200) -> list[sqlite3.Row]:
        return self.conn().execute(
            "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    # ── devices ────────────────────────────────────────────────────────────

    def upsert_device(self, ip: str, mac: str, vendor: str, hostname: str):
        now = time.time()
        self.conn().execute(
            "INSERT INTO devices(ip,mac,vendor,hostname,first_seen,last_seen) "
            "VALUES(?,?,?,?,?,?) ON CONFLICT(mac) DO UPDATE SET "
            "ip=excluded.ip, hostname=excluded.hostname, last_seen=excluded.last_seen",
            (ip, mac, vendor, hostname, now, now)
        )
        self.conn().commit()

    def get_devices(self) -> list[sqlite3.Row]:
        return self.conn().execute(
            "SELECT * FROM devices ORDER BY last_seen DESC"
        ).fetchall()

    # ── settings ───────────────────────────────────────────────────────────

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn().execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        self.conn().execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value)
        )
        self.conn().commit()

    # ── limits ─────────────────────────────────────────────────────────────

    def get_limits(self) -> list[sqlite3.Row]:
        return self.conn().execute(
            "SELECT * FROM usage_limits ORDER BY period"
        ).fetchall()

    def set_limit(self, period: str, limit_bytes: int, enabled: bool = True):
        self.conn().execute(
            "INSERT OR REPLACE INTO usage_limits(period,limit_bytes,enabled) "
            "VALUES(?,?,?)", (period, limit_bytes, 1 if enabled else 0)
        )
        self.conn().commit()

    # ── maintenance ────────────────────────────────────────────────────────

    def prune_old_data(self, keep_days: int = 365):
        cutoff = time.time() - keep_days * 86400
        self.conn().execute(
            "DELETE FROM network_usage WHERE timestamp<?", (cutoff,)
        )
        self.conn().execute(
            "DELETE FROM connection_logs WHERE timestamp<?", (cutoff,)
        )
        self.conn().commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

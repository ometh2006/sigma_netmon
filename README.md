# Σ Dev Network Monitor

> **A professional, real-time Windows network monitoring application** with live bandwidth charts, per-application usage tracking, historical statistics, diagnostics tools, LAN device scanning, and an intelligent alert system.

![Dark Mode Dashboard](docs/screenshot_dark.png)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Real-time Charts** | Line & bar charts, 1-second refresh, per-interface |
| **Bandwidth Statistics** | Today / Week / Month / Year / All-time with SQLite storage |
| **Per-App Usage** | See which process is using bandwidth, with PID and speed |
| **Active Connections** | TCP/UDP table with DNS reverse lookup & state colors |
| **Diagnostics** | Continuous ping monitor, traceroute, DNS lookup |
| **LAN Scanner** | ARP-based device discovery with vendor lookup |
| **Alert System** | Speed limits, spike detection, Windows toast notifications |
| **Data Export** | CSV, JSON, and styled PDF reports |
| **System Tray** | Live speed tooltip, pause/resume, runs in background |
| **Themes** | Dark (default) & Light mode with gradient accents |
| **100% Local** | No internet connection required, no telemetry |

---

## 🚀 Quick Start (End Users)

1. Download `SigmaNetMon.exe` from the [Releases](../../releases) page
2. Double-click to run — **no installation required**
3. The app opens its dashboard and also appears in the system tray
4. Close the window to minimise to tray; right-click tray icon → **Exit** to quit

> **Note:** For full per-process network statistics, run as **Administrator**.

---

## 🔧 Development Setup

### Requirements

- Python 3.11 or 3.12
- Windows 10 / 11 (for full feature set)

### Install

```bash
git clone https://github.com/your-org/sigma-netmon.git
cd sigma-netmon

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run (development)

```bash
python src/main.py
```

### Build `.exe` locally

```bash
pyinstaller sigma_netmon.spec --noconfirm --clean
# Output: dist/SigmaNetMon.exe
```

---

## 🏗 Project Structure

```
sigma-netmon/
├── src/
│   ├── main.py               ← Entry point
│   ├── mainwindow.py         ← Main window + sidebar nav + tray
│   ├── core/
│   │   ├── network_monitor.py  ← psutil-based monitoring thread
│   │   ├── db_manager.py       ← SQLite persistence
│   │   ├── alert_manager.py    ← Threshold detection & notifications
│   │   └── export_manager.py   ← CSV / JSON / PDF export
│   ├── ui/
│   │   ├── dashboard_tab.py    ← Live charts & speed cards
│   │   ├── statistics_tab.py   ← Historical usage & export
│   │   ├── processes_tab.py    ← Per-application network usage
│   │   ├── connections_tab.py  ← Active TCP/UDP connections
│   │   ├── diagnostics_tab.py  ← Ping / traceroute / DNS
│   │   ├── devices_tab.py      ← LAN device ARP scanner
│   │   ├── alerts_tab.py       ← Alert config & history
│   │   ├── settings_tab.py     ← App settings
│   │   └── tray_icon.py        ← System tray
│   └── styles/
│       └── themes.py           ← Dark & light QSS stylesheets
├── resources/                  ← Icons / assets
├── .github/
│   └── workflows/
│       └── build.yml           ← CI: build .exe + create release
├── sigma_netmon.spec           ← PyInstaller spec
├── requirements.txt
└── README.md
```

---

## ⚙ Configuration

All settings are stored in `%APPDATA%\SigmaNetMon\netmon.db` (SQLite). The **Settings** tab lets you change:

- **Theme** – Dark / Light
- **Network Interface** – All, Ethernet, Wi-Fi, VPN, etc.
- **Update Interval** – 0.5 s to 60 s
- **Data Retention** – how many days to keep history
- **Start Minimised** – launch directly to tray

---

## 🔔 Alerts

Configure in the **Alerts** tab:

| Alert Type | Condition |
|---|---|
| Bandwidth Limit | DL or UL speed exceeds threshold (MB/s) |
| Traffic Spike | Instant speed > N× rolling average |
| Connection Lost | Connections drop to 0 |
| Daily / Monthly Quota | Usage exceeds defined GB limit |

Notifications: Windows toast, sound beep, database log.

---

## 📤 Export Formats

| Format | Contents |
|---|---|
| **CSV** | Daily usage table (date, download, upload, total) |
| **JSON** | Summary + daily breakdown with raw byte values |
| **PDF** | Styled branded report with summary + daily table |

---

## 🚢 CI/CD (GitHub Actions)

Every push to `main` runs:

1. **Build** – installs deps, runs PyInstaller → `dist/SigmaNetMon.exe`
2. **Artifact upload** – available for 30 days under *Actions → Artifacts*
3. **Auto-release** – on `git push --tags v1.2.3` a GitHub Release is created with the `.exe` attached

---

## 🛡 Privacy

- **All data stays on your machine** – stored in `%APPDATA%\SigmaNetMon\`
- No analytics, no telemetry, no cloud sync
- Fully offline – works without internet

---

## 📋 Dependencies

| Package | Purpose |
|---|---|
| PyQt6 | UI framework |
| pyqtgraph | Fast real-time charts |
| psutil | Network / process data |
| reportlab | PDF export |
| scapy | Advanced packet info (optional) |
| netifaces | Network interface enumeration |
| PyInstaller | Single-file .exe packaging |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

<div align="center">

<img src="https://img.shields.io/badge/%CE%A3-Dev%20Network%20Monitor-7c3aed?style=for-the-badge&logo=windows&logoColor=white" alt="Σ Dev Network Monitor" height="42"/>

# Σ Dev Network Monitor

**Professional real-time network monitoring for Windows — built for developers, power users, and sysadmins.**


[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078d4?style=flat-square&logo=windows)](../../releases)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=flat-square)](LICENSE)
[![No Telemetry](https://img.shields.io/badge/Telemetry-None-ef4444?style=flat-square&logo=shield)](README.md)

<br/>

> Monitor every byte. Know every process. Own your network.

<br/>

[**⬇ Download .exe**](../../releases/latest) &nbsp;·&nbsp; [**📖 How to Use**](#-how-to-use) &nbsp;·&nbsp; [**🛠 Build from Source**](#-build-from-source) &nbsp;·&nbsp; [**🗺 Roadmap**](#-roadmap)

</div>

---

## 🌟 Why Σ Dev Network Monitor?

Most network monitors are either too simple (just a speed widget) or too expensive (GlassWire Pro, NetLimiter). This project fills that gap — a **free, open-source, feature-complete** alternative with a modern UI, built entirely in Python.

| Feature | Σ NetMon | Task Manager | GlassWire Free |
|---|:---:|:---:|:---:|
| Real-time speed charts | ✅ | ⚠️ basic | ✅ |
| Per-application usage | ✅ | ✅ | ✅ |
| Historical stats (SQLite) | ✅ | ❌ | ✅ |
| Ping / Traceroute / DNS tools | ✅ | ❌ | ❌ |
| LAN device scanner | ✅ | ❌ | ❌ |
| Export CSV / JSON / PDF | ✅ | ❌ | ❌ |
| Configurable alert system | ✅ | ❌ | ✅ |
| Dark + Light themes | ✅ | ❌ | ⚠️ |
| 100% offline / no telemetry | ✅ | ✅ | ❌ |
| **Free & open source** | ✅ | ✅ | ❌ |

---

## ✨ Features

<details open>
<summary><b>📊 Real-Time Dashboard</b></summary>

- Live download & upload speed with **1-second refresh**
- Switchable **line chart** and **bar chart** views
- Per-interface monitoring: Ethernet, Wi-Fi, VPN, virtual adapters
- Stat cards: current speeds, packets/sec, active connection count
- Rolling 2-minute chart history

</details>

<details>
<summary><b>📈 Bandwidth Statistics</b></summary>

- Historical usage stored in a local **SQLite database**
- Periods: **Today · Week · Month · Year · All-Time**
- Daily breakdown bar chart with date labels
- Summary: Total DL/UL, Peak Speed, Average Speed
- Data auto-pruned after configurable retention period

</details>

<details>
<summary><b>🔄 Per-Application Usage</b></summary>

- Ranks all running processes by bandwidth consumption
- Shows: app name, PID, download speed, upload speed, connection count
- Auto-refreshes every 2 seconds, sortable by any column
- _(Full per-process speeds require Administrator mode on Windows)_

</details>

<details>
<summary><b>🔌 Active Connections</b></summary>

- Real-time table of all TCP/UDP connections
- Shows: process, PID, protocol, local/remote address, remote hostname, port, state
- Async DNS reverse lookup (non-blocking)
- Filter by: search term, protocol (TCP/UDP), connection state
- Color-coded states (ESTABLISHED, LISTEN, TIME_WAIT, etc.)

</details>

<details>
<summary><b>🔧 Diagnostics Tools</b></summary>

- **Ping Monitor** — continuous ping to any host, live latency chart, packet loss %, jitter
- **Traceroute** — visual hop-by-hop path to destination
- **DNS Lookup** — A record, AAAA record, PTR reverse lookup, resolution time

</details>

<details>
<summary><b>📡 LAN Device Scanner</b></summary>

- ARP-based discovery of all devices on your local network
- Shows: IP, MAC address, vendor (OUI lookup), hostname
- Results persisted in database with first/last seen timestamps

</details>

<details>
<summary><b>🔔 Alert System</b></summary>

- **Speed limits** — alert when DL or UL exceeds threshold (MB/s)
- **Traffic spike** — alert when speed is N× the rolling average
- **Connection lost** — alert when active connections drop to 0
- **Usage quotas** — daily and monthly GB limits
- Delivery: Windows toast notification + sound beep + database log

</details>

<details>
<summary><b>📤 Export Reports</b></summary>

- **CSV** — spreadsheet-ready daily usage table
- **JSON** — structured data with summary + daily breakdown
- **PDF** — branded, styled report with summary table and daily breakdown

</details>

---

## ⬇ Installation

### Option A — Download the .exe _(Recommended)_

1. Go to [**Releases → Latest**](../../releases/latest)
2. Download `SigmaNetMon.exe`
3. Double-click to run — **no installer, no setup, no .NET required**
4. The app appears in your taskbar and system tray instantly

> ✅ Single portable file. Works on any Windows 10 / 11 machine (x64).

### Option B — Run from Python Source

See the full guide in [**Build from Source**](#-build-from-source) below.

---

## 📖 How to Use

### First Launch

When you open the app:

1. The **Dashboard** tab loads with live speed charts running immediately
2. A **Σ tray icon** appears near your system clock (bottom-right)
3. Monitoring starts on **All** interfaces by default — no configuration needed

---

### Navigation

Use the **left sidebar** to move between sections:

| Tab | What to do there |
|---|---|
| 📊 **Dashboard** | Watch real-time charts, switch interface or chart style |
| 📈 **Statistics** | Select a time period, review usage history, export reports |
| 🔄 **Processes** | See which app is consuming the most bandwidth |
| 🔌 **Connections** | View all live TCP/UDP connections, filter by protocol or state |
| 🔧 **Diagnostics** | Run ping monitor, traceroute, or DNS lookup |
| 📡 **Devices** | Click **Scan Network** to discover devices on your LAN |
| 🔔 **Alerts** | Configure speed limits and quotas, view alert history |
| ⚙ **Settings** | Change theme, interface, update interval, data retention |

---

### Common Tasks

**Monitor a specific adapter (Wi-Fi only, for example)**
> Dashboard tab → Interface dropdown → select `Wi-Fi`

**See which app is eating your bandwidth**
> Go to the **Processes** tab — it auto-sorts by highest usage

**Set a speed alert**
> Alerts tab → set Download Limit (e.g. `50 MB/s`) → Save Configuration
> Leave at `0` to disable

**Export a monthly report**
> Statistics tab → select `Month` → click **PDF** or **CSV** → choose save path

**Minimise to background**
> Click the window's ✕ close button — the app stays running in the system tray
> Right-click the Σ tray icon → **Exit** to fully quit

---

### System Tray Reference

| Action | Result |
|---|---|
| Hover over Σ icon | Shows current DL / UL speeds + connection count |
| Double-click | Opens the main dashboard |
| Right-click → Open | Opens the main dashboard |
| Right-click → Pause | Stops data collection (resumes when clicked again) |
| Right-click → Settings | Opens main window on Settings tab |
| Right-click → Exit | Closes the app completely |

---

## 🛠 Build from Source

### Prerequisites

| Requirement | Minimum Version |
|---|---|
| Windows | 10 or 11 (x64) |
| Python | 3.11 or 3.12 |
| Git | Any recent version |

### Step-by-Step

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sigma-netmon.git
cd sigma-netmon

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Run the app in development mode
python src/main.py
```

### Build the portable `.exe`

```bash
pyinstaller sigma_netmon.spec --noconfirm --clean
```

The output is at `dist/SigmaNetMon.exe` — a single portable file with no external dependencies.

> **Admin note:** To enable full per-process network stats on Windows, the app needs to run as Administrator. You can enable this in the spec file by setting `uac_admin=True` in the `EXE()` call, which will trigger a UAC prompt on launch.

---

## 🚀 Releasing a New Version

Releases are fully automated via GitHub Actions.

```bash
# 1. Commit your changes
git add .
git commit -m "chore: release v1.2.0"

# 2. Tag it with a version number (must start with 'v')
git tag v1.2.0

# 3. Push the commit and tag
git push origin main --tags
```

GitHub Actions will automatically:
- ✅ Spin up a Windows runner
- ✅ Install dependencies and run PyInstaller
- ✅ Run the linter (syntax errors fail the build; style warnings are advisory)
- ✅ Create a GitHub Release titled `Σ Dev Network Monitor v1.2.0`
- ✅ Attach `SigmaNetMon.exe` to the release for public download

You can also trigger a manual build at any time from the **Actions** tab → **Build Windows Installer** → **Run workflow**.

---

## 🗂 Project Structure

```
sigma-netmon/
│
├── src/
│   ├── main.py                 ← Entry point, DPI-aware Windows launcher
│   ├── mainwindow.py           ← Main window, sidebar nav, tray, DB write loop
│   │
│   ├── core/
│   │   ├── network_monitor.py  ← Background QThread: psutil stats + rolling history
│   │   ├── db_manager.py       ← SQLite: usage, alerts, devices, settings, limits
│   │   ├── alert_manager.py    ← Threshold checks, EMA spike detection, notifications
│   │   └── export_manager.py   ← CSV / JSON / PDF report generation
│   │
│   ├── ui/
│   │   ├── dashboard_tab.py    ← Live pyqtgraph charts + stat cards
│   │   ├── statistics_tab.py   ← Historical charts + export buttons
│   │   ├── processes_tab.py    ← Per-process bandwidth table
│   │   ├── connections_tab.py  ← TCP/UDP connection viewer + async DNS
│   │   ├── diagnostics_tab.py  ← Ping / traceroute / DNS tools
│   │   ├── devices_tab.py      ← ARP LAN scanner
│   │   ├── alerts_tab.py       ← Alert config + history log
│   │   ├── settings_tab.py     ← App preferences
│   │   └── tray_icon.py        ← System tray icon + context menu
│   │
│   └── styles/
│       └── themes.py           ← Dark & light QSS stylesheets with gradients
│
├── resources/                  ← Place icon.ico here for a custom app icon
├── .github/
│   └── workflows/
│       └── build.yml           ← CI: build .exe → auto GitHub Release on tag push
│
├── sigma_netmon.spec           ← PyInstaller one-file .exe build spec
├── requirements.txt            ← Python dependencies
└── README.md
```

---

## ⚙ Configuration & Data Storage

All data is stored **100% locally** — the app never needs an internet connection.

| Item | Location |
|---|---|
| Database | `%APPDATA%\SigmaNetMon\netmon.db` |
| All settings | Stored inside the database (`settings` table) |
| Alert history | Stored inside the database (`alerts` table) |
| Device history | Stored inside the database (`devices` table) |
| Usage history | Stored inside the database (`network_usage` table) |

To fully reset the app, delete the folder: `%APPDATA%\SigmaNetMon\`

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| [PyQt6](https://pypi.org/project/PyQt6/) | ≥ 6.4 | UI framework (widgets, threads, signals) |
| [pyqtgraph](https://pyqtgraph.readthedocs.io/) | ≥ 0.13 | Real-time GPU-accelerated charts |
| [psutil](https://github.com/giampaolo/psutil) | ≥ 5.9 | Network stats, process list, connections |
| [reportlab](https://www.reportlab.com/) | ≥ 3.6 | PDF report generation |
| [scapy](https://scapy.net/) | ≥ 2.5 | Advanced packet capture _(optional)_ |
| [netifaces](https://pypi.org/project/netifaces/) | ≥ 0.11 | Network interface enumeration |
| [PyInstaller](https://pyinstaller.org/) | ≥ 5.13 | Single-file `.exe` packaging |

---

## 🗺 Roadmap

- [ ] **v1.1** — Floating always-on-top mini speed widget
- [ ] **v1.1** — Country / city lookup for remote IPs (MaxMind GeoLite2)
- [ ] **v1.2** — Built-in internet speed test (Speedtest.net / LibreSpeed)
- [ ] **v1.2** — Protocol breakdown chart (HTTP / HTTPS / DNS / QUIC traffic share)
- [ ] **v1.3** — Per-application bandwidth limiter (Windows QoS API)
- [ ] **v1.3** — Raw packet capture viewer (Npcap integration)
- [ ] **v2.0** — NSIS installer with Windows startup shortcut option

Have an idea? [Open an issue](../../issues/new) or submit a pull request — contributions are welcome!

---

## 🤝 Contributing

```bash
# 1. Fork this repo and clone your fork
git clone https://github.com/YOUR_USERNAME/sigma-netmon.git
cd sigma-netmon

# 2. Set up the environment
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run and verify
python src/main.py

# 4. Make your changes, then open a Pull Request
```

**Code style guidelines:**
- PEP 8, max line length 100
- Type hints encouraged
- Each new tab should implement an `apply_theme(dark: bool)` method
- Test both Dark and Light mode before submitting

---

## 🛡 Privacy & Security

- **No data leaves your machine.** Ever. No analytics, no crash reporting, no telemetry.
- All collected network data lives in a SQLite file you fully control.
- The app never opens outbound connections except when *you* explicitly run a ping / traceroute / DNS lookup.
- The full source code is here to audit.

---

## 📄 License

```
MIT License — Copyright (c) 2024 Σ Dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
```

See [LICENSE](LICENSE) for full text.

---

<div align="center">

Built with ♥ in Python · PyQt6 · pyqtgraph · psutil

[⬆ Back to top](#-dev-network-monitor)

</div>

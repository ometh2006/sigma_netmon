DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0a0e1a;
    color: #e2e8f0;
}

QWidget {
    background-color: #0a0e1a;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

/* ── Sidebar ── */
#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f1629, stop:1 #070b14);
    border-right: 1px solid #1e2d4d;
    min-width: 200px;
    max-width: 200px;
}

/* ── Nav buttons ── */
QPushButton#NavBtn {
    background: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 8px;
}
QPushButton#NavBtn:hover {
    background: rgba(124, 58, 237, 0.15);
    color: #e2e8f0;
}
QPushButton#NavBtn:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(124,58,237,0.35), stop:1 rgba(6,182,212,0.20));
    color: #a78bfa;
    border-left: 3px solid #7c3aed;
}

/* ── Cards / panels ── */
QFrame#Card {
    background: #0f1629;
    border: 1px solid #1e2d4d;
    border-radius: 12px;
    padding: 4px;
}

/* ── Top bar ── */
QFrame#TopBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0f1629, stop:1 #0a0e1a);
    border-bottom: 1px solid #1e2d4d;
    min-height: 52px;
    max-height: 52px;
}

/* ── Labels ── */
QLabel#Title {
    font-size: 22px;
    font-weight: 700;
    color: transparent;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #06b6d4);
    -qt-background-role: none;
}
QLabel#SectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #e2e8f0;
}
QLabel#StatValue {
    font-size: 28px;
    font-weight: 800;
    color: #a78bfa;
}
QLabel#StatLabel {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QLabel#SpeedDown {
    font-size: 24px;
    font-weight: 700;
    color: #06b6d4;
}
QLabel#SpeedUp {
    font-size: 24px;
    font-weight: 700;
    color: #f59e0b;
}
QLabel#SubLabel {
    color: #64748b;
    font-size: 11px;
}

/* ── Tables ── */
QTableWidget {
    background: #0f1629;
    alternate-background-color: #111827;
    color: #e2e8f0;
    gridline-color: #1e2d4d;
    border: 1px solid #1e2d4d;
    border-radius: 8px;
    selection-background-color: rgba(124,58,237,0.25);
    selection-color: #e2e8f0;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
}
QHeaderView::section {
    background: #070b14;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #1e2d4d;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── ComboBox ── */
QComboBox {
    background: #111827;
    color: #e2e8f0;
    border: 1px solid #1e2d4d;
    border-radius: 6px;
    padding: 6px 10px;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #111827;
    color: #e2e8f0;
    selection-background-color: rgba(124,58,237,0.3);
    border: 1px solid #1e2d4d;
}

/* ── Buttons ── */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #6d28d9);
    color: #fff;
    border: none;
    border-radius: 7px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8b5cf6, stop:1 #7c3aed);
}
QPushButton:pressed {
    background: #6d28d9;
}
QPushButton#BtnSecondary {
    background: #111827;
    color: #94a3b8;
    border: 1px solid #1e2d4d;
}
QPushButton#BtnSecondary:hover {
    background: #1e2d4d;
    color: #e2e8f0;
}
QPushButton#BtnDanger {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ef4444, stop:1 #dc2626);
    color: #fff;
}
QPushButton#BtnSuccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #10b981, stop:1 #059669);
    color: #fff;
}

/* ── Line edit / input ── */
QLineEdit {
    background: #111827;
    color: #e2e8f0;
    border: 1px solid #1e2d4d;
    border-radius: 6px;
    padding: 7px 12px;
}
QLineEdit:focus {
    border-color: #7c3aed;
}

/* ── Spin box ── */
QSpinBox, QDoubleSpinBox {
    background: #111827;
    color: #e2e8f0;
    border: 1px solid #1e2d4d;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ── Scroll bars ── */
QScrollBar:vertical {
    background: #070b14;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #1e2d4d;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #7c3aed; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #070b14;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #1e2d4d;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #7c3aed; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Tab (for diagnostics / sub-tabs) ── */
QTabWidget::pane {
    border: 1px solid #1e2d4d;
    border-radius: 8px;
    background: #0f1629;
}
QTabBar::tab {
    background: #070b14;
    color: #64748b;
    padding: 8px 20px;
    border: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #0f1629; color: #a78bfa; }
QTabBar::tab:hover { color: #e2e8f0; }

/* ── Status bar ── */
QStatusBar {
    background: #070b14;
    color: #64748b;
    border-top: 1px solid #1e2d4d;
    font-size: 12px;
}

/* ── Checkbox ── */
QCheckBox { color: #e2e8f0; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 2px solid #1e2d4d;
    background: #111827;
}
QCheckBox::indicator:checked {
    background: #7c3aed;
    border-color: #7c3aed;
}

/* ── Group box ── */
QGroupBox {
    color: #94a3b8;
    font-weight: 600;
    border: 1px solid #1e2d4d;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #94a3b8;
    font-size: 12px;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #1e2d4d;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #7c3aed;
    width: 16px; height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::sub-page:horizontal { background: #7c3aed; border-radius: 2px; }

/* ── Text edit / log ── */
QTextEdit, QPlainTextEdit {
    background: #070b14;
    color: #e2e8f0;
    border: 1px solid #1e2d4d;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

/* ── Progress bar ── */
QProgressBar {
    background: #111827;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #06b6d4);
    border-radius: 4px;
}

/* ── ToolTip ── */
QToolTip {
    background: #111827;
    color: #e2e8f0;
    border: 1px solid #1e2d4d;
    border-radius: 6px;
    padding: 6px 10px;
}
"""

LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #f1f5f9;
    color: #0f172a;
}
QWidget {
    background-color: #f1f5f9;
    color: #0f172a;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #f8fafc);
    border-right: 1px solid #e2e8f0;
    min-width: 200px;
    max-width: 200px;
}
QPushButton#NavBtn {
    background: transparent;
    color: #64748b;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 8px;
}
QPushButton#NavBtn:hover {
    background: rgba(124, 58, 237, 0.08);
    color: #0f172a;
}
QPushButton#NavBtn:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(124,58,237,0.15), stop:1 rgba(6,182,212,0.10));
    color: #7c3aed;
    border-left: 3px solid #7c3aed;
}
QFrame#Card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 4px;
}
QFrame#TopBar {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    min-height: 52px;
    max-height: 52px;
}
QLabel#SectionTitle { font-size: 14px; font-weight: 700; color: #0f172a; }
QLabel#StatValue { font-size: 28px; font-weight: 800; color: #7c3aed; }
QLabel#StatLabel { font-size: 11px; color: #94a3b8; }
QLabel#SpeedDown { font-size: 24px; font-weight: 700; color: #0891b2; }
QLabel#SpeedUp { font-size: 24px; font-weight: 700; color: #d97706; }
QLabel#SubLabel { color: #94a3b8; font-size: 11px; }
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    color: #0f172a;
    gridline-color: #e2e8f0;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    selection-background-color: rgba(124,58,237,0.12);
    selection-color: #0f172a;
}
QTableWidget::item { padding: 6px 10px; border: none; }
QHeaderView::section {
    background: #f8fafc;
    color: #64748b;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 11px;
}
QComboBox {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 10px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #0f172a;
    selection-background-color: rgba(124,58,237,0.1);
    border: 1px solid #e2e8f0;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #6d28d9);
    color: #fff;
    border: none;
    border-radius: 7px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover { background: #8b5cf6; }
QPushButton#BtnSecondary {
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
}
QPushButton#BtnSecondary:hover { background: #e2e8f0; color: #0f172a; }
QPushButton#BtnDanger { background: #ef4444; color: #fff; }
QPushButton#BtnSuccess { background: #10b981; color: #fff; }
QLineEdit {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 7px 12px;
}
QLineEdit:focus { border-color: #7c3aed; }
QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 10px;
}
QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; margin: 0; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #7c3aed; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #f1f5f9; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #cbd5e1; border-radius: 4px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #7c3aed; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff; }
QTabBar::tab { background: #f8fafc; color: #94a3b8; padding: 8px 20px; border: none;
    border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
QTabBar::tab:selected { background: #ffffff; color: #7c3aed; }
QStatusBar { background: #ffffff; color: #94a3b8; border-top: 1px solid #e2e8f0; font-size: 12px; }
QCheckBox { color: #0f172a; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 2px solid #e2e8f0; background: #fff; }
QCheckBox::indicator:checked { background: #7c3aed; border-color: #7c3aed; }
QGroupBox { color: #64748b; font-weight: 600; border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 12px; padding-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; color: #64748b; font-size: 12px; }
QTextEdit, QPlainTextEdit { background: #f8fafc; color: #0f172a; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px; font-family: 'Consolas', monospace; font-size: 12px; }
QProgressBar { background: #e2e8f0; border: none; border-radius: 4px; height: 6px; color: transparent; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #06b6d4); border-radius: 4px; }
QToolTip { background: #ffffff; color: #0f172a; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 10px; }
"""


def get_theme(name: str) -> str:
    return DARK_THEME if name == "dark" else LIGHT_THEME

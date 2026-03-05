"""
Export manager: CSV / JSON / PDF report generation.
"""

import csv
import json
import time
import os
from datetime import datetime
from pathlib import Path


def _fmt_bytes(b: int) -> str:
    if b >= 1_073_741_824:
        return f"{b/1_073_741_824:.2f} GB"
    if b >= 1_048_576:
        return f"{b/1_048_576:.2f} MB"
    if b >= 1_024:
        return f"{b/1_024:.1f} KB"
    return f"{b} B"


class ExportManager:
    def __init__(self, db_manager):
        self.db = db_manager

    # ── public API ─────────────────────────────────────────────────────────

    def export_csv(self, period: str, output_path: str) -> str:
        rows = self.db.get_daily_usage(days=self._period_days(period))
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Download", "Upload", "Total"])
            for r in rows:
                dl, ul = r["dl"], r["ul"]
                writer.writerow([
                    r["date"],
                    _fmt_bytes(dl),
                    _fmt_bytes(ul),
                    _fmt_bytes(dl + ul),
                ])
        return output_path

    def export_json(self, period: str, output_path: str) -> str:
        rows = self.db.get_daily_usage(days=self._period_days(period))
        summary = self.db.get_aggregated_usage(period)
        data = {
            "generated": datetime.now().isoformat(),
            "period": period,
            "summary": {
                "total_download": _fmt_bytes(summary["dl"]),
                "total_upload": _fmt_bytes(summary["ul"]),
                "peak_download": f"{summary['peak_dl']/1e6:.2f} MB/s",
                "peak_upload": f"{summary['peak_ul']/1e6:.2f} MB/s",
                "avg_download": f"{summary['avg_dl']/1e6:.2f} MB/s",
            },
            "daily": [
                {"date": r["date"],
                 "download_bytes": r["dl"],
                 "upload_bytes": r["ul"]}
                for r in rows
            ],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return output_path

    def export_pdf(self, period: str, output_path: str) -> str:
        """Generate a styled PDF report using reportlab."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            )
        except ImportError:
            raise RuntimeError(
                "reportlab is required for PDF export. "
                "Install it with: pip install reportlab"
            )

        rows = self.db.get_daily_usage(days=self._period_days(period))
        summary = self.db.get_aggregated_usage(period)

        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "title", parent=styles["Title"],
            textColor=colors.HexColor("#7c3aed"),
            fontSize=24, spaceAfter=6
        )
        h2_style = ParagraphStyle(
            "h2", parent=styles["Heading2"],
            textColor=colors.HexColor("#0f172a"),
            fontSize=14, spaceBefore=14, spaceAfter=6
        )
        body_style = styles["Normal"]

        content = []

        # Header
        content.append(Paragraph("Σ Dev Network Monitor", title_style))
        content.append(Paragraph(
            f"Report Period: <b>{period.capitalize()}</b> — "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            body_style
        ))
        content.append(Spacer(1, 0.5*cm))

        # Summary table
        content.append(Paragraph("Summary", h2_style))
        summary_data = [
            ["Metric", "Value"],
            ["Total Download", _fmt_bytes(summary["dl"])],
            ["Total Upload",   _fmt_bytes(summary["ul"])],
            ["Peak Download",  f"{summary['peak_dl']/1e6:.2f} MB/s"],
            ["Peak Upload",    f"{summary['peak_ul']/1e6:.2f} MB/s"],
            ["Avg Download",   f"{summary['avg_dl']/1e6:.2f} MB/s"],
        ]
        s_tbl = Table(summary_data, colWidths=[8*cm, 8*cm])
        s_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.HexColor("#f8f8fc"), colors.white]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTSIZE",   (0, 0), (-1, -1), 11),
            ("PADDING",    (0, 0), (-1, -1), 8),
        ]))
        content.append(s_tbl)
        content.append(Spacer(1, 0.5*cm))

        # Daily breakdown
        if rows:
            content.append(Paragraph("Daily Usage", h2_style))
            daily_data = [["Date", "Download", "Upload", "Total"]]
            for r in rows:
                dl, ul = r["dl"], r["ul"]
                daily_data.append([
                    r["date"], _fmt_bytes(dl),
                    _fmt_bytes(ul), _fmt_bytes(dl + ul)
                ])
            d_tbl = Table(daily_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
            d_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#06b6d4")),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.HexColor("#f8f8fc"), colors.white]),
                ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("FONTSIZE",   (0, 0), (-1, -1), 10),
                ("PADDING",    (0, 0), (-1, -1), 7),
            ]))
            content.append(d_tbl)

        doc.build(content)
        return output_path

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _period_days(period: str) -> int:
        return {"today": 1, "week": 7, "month": 30,
                "year": 365, "alltime": 3650}.get(period, 30)

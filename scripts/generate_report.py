"""
generate_report.py
------------------
Reusable function generate_pdf(vuln_data, md_path) that:
• Builds a nicely wrapped PDF via ReportLab/Platypus
• Optionally parses output_report.md for Risk / Affected / Remediation
"""

import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
)

# --------------------------------------------------------------------
# Helper: parse reports/output_report.md into a dict
# --------------------------------------------------------------------
def parse_md(md_file: Path) -> dict:
    """Return {'risk': ..., 'affected': ..., 'remediation': ...} or empty dict."""
    if not md_file.exists():
        return {}
    out = {}
    with md_file.open(encoding="utf-8") as fh:
        for line in fh:
            if ":" in line:
                key, val = line.split(":", 1)
                out[key.strip().lower()] = val.strip()
    return out


# --------------------------------------------------------------------
# Main function to be imported by main.py
# --------------------------------------------------------------------
def generate_pdf(
    vuln_data: dict,
    md_path: Optional[Path] = None,
    out_pdf: Optional[Path] = None,
):
    base_dir = Path(__file__).resolve().parent.parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    md_path = md_path or reports_dir / "output_report.md"
    out_pdf = out_pdf or reports_dir / "output_report.pdf"

    # Parse Risk / Affected / Remediation if the MD file exists
    md_sections = parse_md(md_path)

    # -------------------- Build PDF -------------------------------
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Heading1Centered",
            parent=styles["Heading1"],
            alignment=1,
        )
    )
    bold = styles["Heading4"]
    normal = styles["BodyText"]

    elements = []

    # Title + timestamp
    elements.append(Paragraph("Vulnerability Report", styles["Heading1Centered"]))
    elements.append(
        Paragraph(
            f"Generated on: {datetime.datetime.now():%Y-%m-%d %H:%M}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 12))

    # Key-value table
    kv_pairs = [
        ("IP", vuln_data["ip"]),
        ("Service", vuln_data["service"]),
        ("Version", vuln_data["version"]),
        ("CVE ID", vuln_data["cve_id"]),
        ("Severity", vuln_data["severity"]),
        ("CVSS Score", vuln_data["cvss"]),
        ("Published", vuln_data["published"]),
        ("CPE", vuln_data["cpe"]),
    ]
    table_data = [
        [Paragraph(f"<b>{k}</b>", bold), Paragraph(str(v), normal)]
        for k, v in kv_pairs
    ]
    table = Table(table_data, colWidths=[40 * mm, None], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 14))

    # Summary
    elements.append(Paragraph("<b>Summary</b>", bold))
    elements.append(Paragraph(vuln_data["summary"], normal))
    elements.append(Spacer(1, 12))

    # Inject Risk / Affected / Remediation from MD (if any)
    for section_key, title in [
        ("risk", "Risk"),
        ("affected", "Affected"),
        ("remediation", "Remediation"),
    ]:
        if section_key in md_sections:
            elements.append(Paragraph(f"<b>{title}</b>", bold))
            elements.append(Paragraph(md_sections[section_key], normal))
            elements.append(Spacer(1, 10))

    # Recommendation (fallback if not already under Remediation)
    if "remediation" not in md_sections:
        elements.append(Paragraph("<b>Recommendation</b>", bold))
        elements.append(Paragraph(vuln_data["recommendation"], normal))

    doc.build(elements)
    print(f"✅ PDF saved to {out_pdf.relative_to(base_dir)}")


# Allow quick CLI test
if __name__ == "__main__":
    import json, sys

    # Example: python scripts/generate_report.py vuln.json
    if len(sys.argv) > 1:
        vuln_data = json.loads(Path(sys.argv[1]).read_text())
    else:
        vuln_data = {"ip": "127.0.0.1", "service": "Demo", "version": "1.0", "cpe": "", "cve_id": "-", "severity": "-", "cvss": "-", "published": "-", "summary": "demo", "recommendation": "update"}
    generate_pdf(vuln_data)

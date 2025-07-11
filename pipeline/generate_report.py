from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf_report(data, llm_summary, output_path="data/Vulnerability_Report.pdf"):
    os.makedirs("data", exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Vulnerability Report", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)

    for item in data:
        ip = item['ip']
        service = item['product'] or "Unknown"
        version = item['version'] or "Unknown"
        cpe = item['cpe'] or "Unknown"

        for vuln in item['vulnerabilities']:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"IP: {ip}", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 10, f"Service: {service}", ln=True)
            pdf.cell(0, 10, f"Version: {version}", ln=True)
            pdf.cell(0, 10, f"CPE: {cpe}", ln=True)
            pdf.cell(0, 10, f"CVE ID: {vuln['cve_id']}", ln=True)
            pdf.cell(0, 10, f"Severity: {vuln['severity']}  |  CVSS: {vuln['score']}", ln=True)
            pdf.multi_cell(0, 10, f"Description: {vuln['description']}")
            if vuln.get("reference"):
                pdf.set_text_color(0, 0, 255)
                pdf.cell(0, 10, f"More Info: {vuln['reference']}", ln=True, link=vuln['reference'])
                pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

    # Summary Section
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Summary & Recommendations", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, llm_summary)

    pdf.output(output_path)

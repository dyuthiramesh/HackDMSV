import datetime
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)
MD_PATH = REPORTS / "output_report.md"

# 1.  Dummy vuln_data (replace with real parsed values later)

vuln_data = {
    "ip": "192.168.1.10",
    "service": "Apache HTTP Server",
    "version": "2.4.29",
    "cpe": "cpe:2.3:a:apache:http_server:2.4.29:*:*:*:*:*:*:*",
    "cve_id": "CVE-2019-0211",
    "severity": "HIGH",
    "cvss": 7.8,
    "published": "2019-03-01",
    "summary": "PLACEHOLDER",
    "recommendation": "Upgrade Apache HTTP Server to version 2.4.41 or later.",
}

# 2.  Load env & get LLM summary

load_dotenv(BASE / ".env")
from scripts.ask_llm import ask_summary_prompt  # noqa: E402

print("🔄  Asking GPT-4 for risk summary …")
llm_summary = ask_summary_prompt(vuln_data)
vuln_data["summary"] = llm_summary

# 3.  Write output_report.md (Risk / Affected / Remediation)

risk_block = f"Risk: {llm_summary}"
affected_block = (
    f"Affected: All users of {vuln_data['service']} version {vuln_data['version']}."
)
rem_block = f"Remediation: {vuln_data['recommendation']}"

MD_PATH.write_text(f"{risk_block}\n\n{affected_block}\n\n{rem_block}\n", encoding="utf-8")
print(f"📝  Markdown saved to {MD_PATH.relative_to(BASE)}")

# 4.  Generate the PDF

from scripts.generate_report import generate_pdf  # noqa: E402

print("🖨  Generating PDF …")
generate_pdf(vuln_data, md_path=MD_PATH)

print("\n🎉  Done! View reports/output_report.pdf")
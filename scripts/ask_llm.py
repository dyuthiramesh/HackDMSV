import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 1.  Load environment variables from ../.env
BASE_DIR = Path(__file__).resolve().parent.parent 
load_dotenv() 

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Add it to .env in the project root "
        "or export it in your shell."
    )

client = OpenAI(api_key=openai_key)

# 2.  LLM helper

def ask_summary_prompt(data: dict) -> str:
    """Return an LLM‑generated risk summary for a single vulnerability."""
    # system prompt
    with open(BASE_DIR / "prompts" / "service_summary_prompt.txt", encoding="utf-8") as f:
        system_prompt = f.read()

    # user prompt
    user_prompt = f"""
Service: {data['service']}
Version: {data['version']}
CPE: {data['cpe']}
CVE ID: {data['cve_id']}
Severity: {data['severity']}
CVSS Score: {data['cvss']}
Published: {data['published']}
Summary: {data['summary']}

Explain the risk, who is affected, and what patch or action should be taken.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# 3.  Main (example usage)

if __name__ == "__main__":
    sample_data = {
        "service": "Apache HTTP Server",
        "version": "2.4.29",
        "cpe": "cpe:2.3:a:apache:http_server:2.4.29:*:*:*:*:*:*:*",
        "cve_id": "CVE-2019-0211",
        "severity": "HIGH",
        "cvss": 7.8,
        "published": "2019-03-01",
        "summary": (
            "Users with write access to a .htaccess file can execute arbitrary "
            "code due to a privilege escalation vulnerability in mod_prefork."
        )
    }

    summary_text = ask_summary_prompt(sample_data)
    print("🔍 LLM Summary:\n", summary_text)

    # 4.  Save the result to ./reports/output_report.md

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)                   # create if missing

    output_path = reports_dir / "output_report.md"
    with open(output_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Vulnerability Summary\n\n")
        md_file.write(summary_text + "\n")

    print(f"✅ Summary saved to {output_path.relative_to(BASE_DIR)}")

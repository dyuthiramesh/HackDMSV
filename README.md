# VulneraTrack — LLM‑Powered Automated Patch‑Management Workflow  

> “Upload an Nmap scan → get an action‑ready, exec‑friendly PDF report in under 2 minutes.”

---

## 📑 Table of Contents
1. [Problem Statement](#problem-statement)  
2. [Solution Overview](#solution-overview)  
3. [System Architecture](#system-architecture)  
4. [Project Structure](#project-structure)  
5. [Prerequisites](#prerequisites)  
6. [Installation](#installation)  
7. [Quick Start Demo](#quick-start-demo)  
8. [Detailed Workflow](#detailed-workflow)  
9. [Extending the Project](#extending-the-project)  
10. [Troubleshooting](#troubleshooting)  
11. [Hackathon Deliverables](#hackathon-deliverables)  
12. [License](#license)

---

## Problem Statement
Manual patch management is slow, error‑prone and often fails to communicate
technical risk to non‑technical stakeholders.  
**Goal:** automate the entire loop—_detect → analyse → prioritise → report_—using Large
Language Models (LLMs) and open‑source tooling.

---

## Solution Overview
1. **Scan** – Security team runs `nmap ‑sV` and uploads the XML.  
2. **Parse** – We extract IP, port, product & version (+ CPE if present).  
3. **Enrich** – Lookup CVEs from NIST NVD and CISA KEV APIs.  
4. **Reason** – GPT‑4o (via OpenAI API) rates severity, explains risk, recommends a patch.  
5. **Document** – We build a Markdown digest and a wrapped, print‑ready PDF via ReportLab.  
6. **Query** – Teams ask natural‑language questions (“Show unpatched critical vulns”) which are converted to SQL and answered on‑the‑fly.

---

## System Architecture

```text
┌────────┐ Nmap XML ┌──────────┐   CPE  ┌────────────┐   CVE JSON
│ Network├──────────▶ XML‑Parser├───┬───▶ NVD / KEV  ├─────────────┐
└────────┘           └──────────┘   │   └────────────┘             │
                                    ▼                               │
                               SQLite DB                            │
                                    │        prompt + context       │
                                    ├──────────────┐                │
                                    ▼              ▼                │
                          LLM (ask_llm.py)   Natural‑lang queries   │
                                    │              ▲                │
                                    ▼              │                │
                 Markdown digest → ReportLab PDF   │                │
                                    │              │                │
                                User Portal  ◀─────┘                │
````

---

## Project Structure

```
vulneratrack/
│
├─ main.py               # one‑command demo driver
├─ requirements.txt
├─ .env          # template for your keys
│
├─ scripts/
│   ├─ ask_llm.py        # prompt → GPT‑4 → summary
│   ├─ generate_report.py# md + vuln_data → PDF (Platypus)
│
├─ templates/            # (optional Jinja2 templates)
├─ reports/              # generated .md and .pdf live here
└─ README.md             # you’re reading it!
```

---

## Prerequisites

* Python 3.9+
* **OpenAI** API key (GPT‑4 / GPT‑4o or 3.5‑turbo)
* Internet access to call NVD/KEV APIs *(optional for offline demo)*

---

## Installation

```bash
git clone https://github.com/dyuthiramesh/vulneratrack.git
cd vulneratrack
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start Demo

```bash
# 1. Get a sample Nmap scan (already provided)
# 2. Run the full pipeline
python main.py
# 3. Open the PDF
open reports/output_report.pdf    # (mac) or start "" reports\output_report.pdf (win)
```

---

from nmap_generate import run_scan_and_parse
from generate_report import generate_pdf_report
from ask_llm import summarize_findings

if __name__ == "__main__":
    target = "scanme.nmap.org"

    print("\n📡 Starting pipeline...")
    enriched_data = run_scan_and_parse(target)

    if not enriched_data:
        print("❌ No data collected. Exiting.")
        exit(1)

    print("\n🧠 Sending to LLM for deeper analysis...\n")
    analysis = summarize_findings(enriched_data)

    print("\n📄 Generating PDF report...\n")
    generate_pdf_report(enriched_data, analysis)

    print("\n✅ All Done! Report saved as data/Vulnerability_Report.pdf")

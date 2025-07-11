import subprocess
import xmltodict
import json
import re
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
NVD_API_KEY = os.getenv("NVD_API_KEY")

def run_nmap(target_ip, xml_output="data/nmap_output.xml"):
    os.makedirs("data", exist_ok=True)
    cmd = [
        # r"C:\Program Files (x86)\Nmap\nmap.exe", "--open",
        r"D:\Nmap\nmap.exe", "--open",
        "-sV", "--version-all", "-T4",
        "--max-retries", "2",
        "--host-timeout", "60s",
        "-oX", xml_output,
        target_ip
    ]
    try:
        print(f"🔍 Scanning {target_ip}...")
        subprocess.run(cmd, check=True)
        print("✅ Nmap scan complete.")
    except Exception as e:
        print(f"❌ Error during Nmap scan: {e}")
        exit(1)

def load_kev_ids():
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        kev_data = requests.get(url).json()
        return {item["cveID"] for item in kev_data["vulnerabilities"]}
    except Exception as e:
        print(f"⚠️ Failed to load KEV list: {e}")
        return set()

def map_severity(score):
    if score is None: return "UNKNOWN"
    elif score >= 9: return "CRITICAL"
    elif score >= 7: return "HIGH"
    elif score >= 4: return "MEDIUM"
    return "LOW"

def convert_to_cpe23(cpe22: str) -> str:
    if not cpe22 or not cpe22.startswith("cpe:/"): return None
    parts = cpe22.replace("cpe:/", "").split(":")
    while len(parts) < 10: parts.append("*")
    return f"cpe:2.3:{':'.join(parts)}"

def guess_cpe(product, version):
    if not product: return None
    normalized = product.lower().strip()
    cpe_map = {
        "apache": ("apache", "http_server"),
        "nginx": ("nginx", "nginx"),
        "openssl": ("openssl", "openssl"),
        "mysql": ("oracle", "mysql"),
        "openssh": ("openbsd", "openssh"),
        "nping": ("unknown", "nping_echo")
    }
    for key in cpe_map:
        if key in normalized:
            vendor, prod = cpe_map[key]
            return f"cpe:2.3:a:{vendor}:{prod}:{version or '*'}:*:*:*:*:*:*:*"
    return f"cpe:2.3:a:unknown:{re.sub(r'[^a-z0-9]', '_', normalized)}:{version or '*'}:*:*:*:*:*:*:*"

def fetch_cves(cpe, kev_ids, limit=5):
    if not cpe: return []
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    try:
        response = requests.get(url, headers=headers, params={"cpeName": cpe, "resultsPerPage": limit})
        response.raise_for_status()
        results = []
        for vuln in response.json().get("vulnerabilities", []):
            cve = vuln["cve"]
            score = None
            if "cvssMetricV31" in cve.get("metrics", {}):
                score = cve["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
            elif "cvssMetricV2" in cve.get("metrics", {}):
                score = cve["metrics"]["cvssMetricV2"][0]["cvssData"]["baseScore"]
            results.append({
                "cve_id": cve["id"],
                "description": next((d["value"] for d in cve["descriptions"] if d["lang"] == "en"), ""),
                "score": score,
                "severity": map_severity(score),
                "kev": cve["id"] in kev_ids,
                "reference": cve.get("references", [{}])[0].get("url")
            })
        return results
    except Exception as e:
        print(f"⚠️ Error fetching CVEs for {cpe}: {e}")
        return []

def parse_nmap_xml(xml_path, kev_ids):
    with open(xml_path, 'r') as f:
        data = xmltodict.parse(f.read())
    results = []
    hosts = data.get("nmaprun", {}).get("host", [])
    if not isinstance(hosts, list): hosts = [hosts]
    for host in hosts:
        ip = host.get("address", {}).get("@addr")
        ports = host.get("ports", {}).get("port", [])
        if not isinstance(ports, list): ports = [ports]
        for port in ports:
            if port.get("state", {}).get("@state") != "open": continue
            service = port.get("service", {})
            product = service.get("@product")
            version = service.get("@version")
            cpe = service.get("cpe")
            if isinstance(cpe, list): cpe = cpe[0]
            cpe = convert_to_cpe23(cpe) if cpe else guess_cpe(product, version)
            print(f"🔍 Fetching CVEs for {cpe}")
            vulns = fetch_cves(cpe, kev_ids)
            time.sleep(1.2)
            results.append({
                "ip": ip,
                "port": port["@portid"],
                "protocol": port["@protocol"],
                "product": product,
                "version": version,
                "cpe": cpe,
                "vulnerabilities": vulns
            })
    return results

def run_scan_and_parse(target_ip):
    run_nmap(target_ip)
    kev_ids = load_kev_ids()
    return parse_nmap_xml("data/nmap_output.xml", kev_ids)

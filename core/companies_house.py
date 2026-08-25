"""companies_house.py — reads CH_API_KEY from environment variable."""
import os, requests
from datetime import datetime

def _fmt_date(iso: str) -> str:
    """Convert '2025-04-14' → '14 April 2025'. Returns original if parse fails."""
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%-d %B %Y")
    except Exception:
        try:
            return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %B %Y").lstrip("0")
        except Exception:
            return iso

BASE = "https://api.companieshouse.gov.uk"

def _auth():
    key = os.environ.get("CH_API_KEY", "")
    if not key:
        raise ValueError("CH_API_KEY environment variable not set.")
    return requests.auth.HTTPBasicAuth(key, "")

def get_company(number: str) -> dict:
    num = number.strip().upper().zfill(8)
    r = requests.get(f"{BASE}/company/{num}", auth=_auth(), timeout=10)
    if r.status_code == 404:
        raise ValueError(f"Company {num} not found on Companies House.")
    r.raise_for_status()
    data = r.json()
    addr = data.get("registered_office_address", {})
    addr_str = ", ".join(p for p in [
        addr.get("address_line_1",""), addr.get("address_line_2",""),
        addr.get("locality",""), addr.get("postal_code",""), addr.get("country","")
    ] if p)
    officers = []
    try:
        ro = requests.get(f"{BASE}/company/{num}/officers", auth=_auth(),
                          params={"items_per_page":20}, timeout=10)
        ro.raise_for_status()
        officers = [{"name": o.get("name",""), "role": o.get("officer_role","")}
                    for o in ro.json().get("items",[]) if not o.get("resigned_on")]
    except Exception:
        pass
    return {
        "company_number": num,
        "company_name": data.get("company_name",""),
        "registered_address": addr_str,
        "incorporation_date": _fmt_date(data.get("date_of_creation","")),
        "sic_codes": data.get("sic_codes",[]),
        "officers": officers,
        "status": data.get("company_status",""),
    }

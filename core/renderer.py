"""
renderer.py — fills the real .docx house templates in templates/docx/ with data,
using docxtpl (Jinja2 for Word). Formatting lives entirely in the template files,
so output matches the reference pack byte-for-byte except for the merged data.

Only documents that have a template here are rendered this way; the rest still
come from the hand-built python-docx modules in templates/*.py.
"""
import io, os, re
from docxtpl import DocxTemplate

TPL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "templates", "docx")

# doc key -> template filename
TEMPLATES = {
    "A1": "A1_title_pages.docx",
    "C2": "C2_board_resolution.docx",
    "C3": "C3_ao_details.docx",
    "C8": "C8_statement_of_truth.docx",
}

_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}


def has_template(key: str) -> bool:
    return key in TEMPLATES and os.path.exists(os.path.join(TPL_DIR, TEMPLATES[key]))


def render(key: str, context: dict) -> bytes:
    tpl = DocxTemplate(os.path.join(TPL_DIR, TEMPLATES[key]))
    tpl.render(context)
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)
    return buf.read()


# ── helpers ──────────────────────────────────────────────────────────────────
_KEEP_UPPER = {"UK", "LLP", "LLC", "PLC", "SECP", "FBR", "HR", "AO", "&"}


def strip_ms(name: str) -> str:
    """Drop a leading "M/S " / "M/s " / "M/s. " prefix."""
    return re.sub(r"^\s*M/?[Ss]\.?\s+", "", name or "").strip()


def _cap_word(tok: str) -> str:
    # capitalise the first letter of each alpha run, lower the rest: "(PRIVATE)" -> "(Private)"
    return re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), tok)


def title_case(name: str) -> str:
    """"JASPER CONSTRUCTION MATERIALS (PRIVATE) LIMITED" -> "Jasper Construction
    Materials (Private) Limited", keeping tokens like UK / LLP uppercase."""
    if not name:
        return ""
    out = []
    for tok in strip_ms(name).split():
        bare = tok.strip("().,").upper()
        out.append(tok.upper() if bare in _KEEP_UPPER else _cap_word(tok))
    return re.sub(r"\bUk\b", "UK", " ".join(out))


def _first(*vals):
    for v in vals:
        if v:
            return v
    return ""


def upper_core(name: str) -> str:
    """"M/S JASPER ... LIMITED" -> "JASPER ... LIMITED" (drop the M/S, upper-case)."""
    return strip_ms(name).upper()


def ddmmyyyy(s: str) -> str:
    """"14 April 2025" -> "14-04-2025"; anything unrecognised is returned unchanged."""
    if not s:
        return ""
    m = re.match(r"\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$", s)
    if m and m.group(2).lower() in _MONTHS:
        return f"{int(m.group(1)):02d}-{_MONTHS[m.group(2).lower()]:02d}-{m.group(3)}"
    return s


def _doc_date(f, x, *keys):
    return _first(*[x.get(k) for k in keys], f.get("application_date"))


# ── context builders ─────────────────────────────────────────────────────────
def build_context(key: str, fields: dict, uk_fields: dict, extra: dict) -> dict:
    extra = extra or {}
    return {
        "A1": _ctx_a1,
        "C2": _ctx_c2,
        "C3": _ctx_c3,
        "C8": _ctx_c8,
    }[key](fields, uk_fields, extra)


def _common(f: dict, uk: dict) -> dict:
    """Fields shared by the C-series letters."""
    parent_name = strip_ms(f.get("parent_name", ""))
    ao_name = f.get("ao_full_name", "")
    uk_name = uk.get("company_name", "")
    return {
        "parent_name": parent_name,
        "parent_name_title": title_case(parent_name),
        "parent_name_upper": upper_core(parent_name),
        "parent_address_full": f.get("parent_address", ""),
        "parent_email": f.get("parent_email", ""),
        "parent_reg_no": f.get("parent_reg_no", ""),
        "parent_ref_no": f.get("parent_ref_no", ""),
        "ao_name": ao_name,
        "ao_name_upper": ao_name.upper(),
        "ao_dob": f.get("ao_dob", ""),
        "ao_passport": f.get("ao_passport", ""),
        "ao_nationality": f.get("ao_nationality") or "Pakistan",
        "ao_position": f.get("ao_position", ""),
        "ao_email": f.get("ao_email", ""),
        "uk_name": uk_name,
        "uk_name_title": title_case(uk_name),
        "uk_number": uk.get("company_number", ""),
        "uk_address": uk.get("registered_address", ""),
        "uk_incorp_date_short": ddmmyyyy(uk.get("incorporation_date", "")),
    }


def _signatory(f: dict):
    """A director who is not the AO, else the last director."""
    ao = f.get("ao_full_name", "").strip().lower()
    directors = f.get("parent_directors", []) or []
    name = next((d for d in directors if d.strip().lower() != ao), "")
    if not name and directors:
        name = directors[-1]
    return name


def _ctx_c3(f: dict, uk: dict, x: dict) -> dict:
    c = _common(f, uk)
    c.update({
        "doc_date": _doc_date(f, x, "c3_doc_date", "doc_date"),
        "ao_uk_title": f.get("ao_uk_title") or "Executive Director",
        "ao_uk_job_type": f.get("ao_uk_job_type") or "Chief executives and senior officials",
        "ao_soc_code": f.get("ao_soc_code") or "1111",
        "ao_going_rate": f.get("ao_going_rate") or "£60,000",
        "ao_going_rate_hourly": f.get("ao_going_rate_hourly") or "£30.77 per hour",
        "reporting_line": _first(f.get("reporting_line"), f.get("reporting_to"),
                                 "The Manager, Operations"),
        "signatory_name": _first(f.get("signatory_name"), _signatory(f)),
        "signatory_title": f.get("signatory_title") or "Managing Director",
    })
    return c


def _ctx_c8(f: dict, uk: dict, x: dict) -> dict:
    c = _common(f, uk)
    c["doc_date"] = _doc_date(f, x, "doc_date")
    return c


def _ctx_c2(f: dict, uk: dict, x: dict) -> dict:
    c = _common(f, uk)
    attendees = (x.get("attendees") or f.get("board_attendees")
                 or f.get("parent_directors") or [])
    chair_full = _first(x.get("chairperson"), f.get("chairperson"), _signatory(f),
                        attendees[0] if attendees else f.get("ao_full_name", ""))
    chair_name = chair_full.split(",")[0].strip()
    c.update({
        "meeting_date": _doc_date(f, x, "meeting_date"),
        "attendees": attendees,
        "chairperson": _first(f.get("chairperson"), chair_name),
        "chairperson_name": chair_name,
    })
    return c


def _ctx_a1(f: dict, uk: dict, x: dict) -> dict:
    parent_name = strip_ms(f.get("parent_name", ""))
    parent_addr = f.get("parent_address", "")
    uk_name = uk.get("company_name", "")
    return {
        "parent_name": parent_name,
        "parent_name_title": title_case(parent_name),
        "parent_secp_uin": _first(f.get("parent_secp_uin"), f.get("parent_reg_no")),
        "parent_incorp_date": _first(f.get("parent_incorp_date"), f.get("parent_reg_date")),
        "parent_reg_no": f.get("parent_reg_no", ""),
        "parent_ref_no": f.get("parent_ref_no", ""),
        "parent_reg_date": f.get("parent_reg_date", ""),
        "parent_reg_address": parent_addr,
        "parent_trading_address": _first(f.get("parent_trading_address"), parent_addr),
        "parent_activity": f.get("parent_activity", ""),
        "parent_website": f.get("parent_website", ""),
        "uk_name": uk_name,
        "uk_name_title": title_case(uk_name),
        "uk_number": uk.get("company_number", ""),
        "uk_incorp_date": uk.get("incorporation_date", ""),
        "uk_address": uk.get("registered_address", ""),
        "uk_trading_address": _first(f.get("uk_trading_address"),
                                     x.get("uk_trading_address"), ""),
        "uk_sic": uk.get("sic_codes", []) or [],
    }

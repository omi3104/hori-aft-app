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
}


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


def title_case(name: str) -> str:
    """"JASPER CONSTRUCTION MATERIALS (PRIVATE) LIMITED" -> "Jasper Construction
    Materials (Private) Limited", keeping tokens like UK / LLP uppercase."""
    if not name:
        return ""
    # strip a leading "M/S " / "M/s " so callers can re-add it consistently
    core = re.sub(r"^\s*M/?[Ss]\.?\s+", "", name).strip()
    out = []
    for tok in core.split():
        bare = tok.strip("().,").upper()
        if bare in _KEEP_UPPER:
            out.append(tok.upper())
        else:
            out.append(tok.capitalize() if tok.isupper() else tok[:1].upper() + tok[1:])
    s = " ".join(out)
    s = re.sub(r"\bUk\b", "UK", s)
    return s


def _first(*vals):
    for v in vals:
        if v:
            return v
    return ""


# ── context builders ─────────────────────────────────────────────────────────
def build_context(key: str, fields: dict, uk_fields: dict, extra: dict) -> dict:
    extra = extra or {}
    if key == "A1":
        return _ctx_a1(fields, uk_fields, extra)
    raise KeyError(key)


def _ctx_a1(f: dict, uk: dict, x: dict) -> dict:
    parent_name = f.get("parent_name", "")
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

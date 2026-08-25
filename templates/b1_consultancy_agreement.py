"""
ANNEX B.1 — Consultancy Agreement
Between parent company + UK subsidiary (Client) and Chisty Law Chambers LLP (Consultant).
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

import tempfile as _tempfile

def _to_bytes(doc):
    """Save document to bytes without writing to disk permanently."""
    import io as _io
    buf = _io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


NAVY = RGBColor(0x1B, 0x3A, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)


def _set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _add_detail_row(table, label, value, col_widths=(2.2, 4.3)):
    row = table.add_row()
    lc, vc = row.cells[0], row.cells[1]
    _set_cell_bg(lc, "1B3A6B")
    lp = lc.paragraphs[0]
    lp.clear()
    lr = lp.add_run(label)
    lr.bold = True
    lr.font.size = Pt(10)
    lr.font.color.rgb = WHITE
    vp = vc.paragraphs[0]
    vp.clear()
    vr = vp.add_run(value)
    vr.font.size = Pt(10)


def _heading(doc, text, size=12, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def _body(doc, text, size=10):
    p = doc.add_paragraph(text)
    for r in p.runs:
        r.font.size = Pt(size)
    return p


def _bullet(doc, text, size=10):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    r.font.size = Pt(size)
    return p


def generate(fields: dict, uk_fields: dict, output_path: str, agreement_date: str = ""):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    _heading(doc, "CONSULTANCY AGREEMENT", size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    date_str = agreement_date or fields.get("application_date", "")
    _body(doc, f"This Agreement is made on the {date_str}, by and between:")
    doc.add_paragraph()

    # Parent + UK subsidiary table
    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.columns[0].width = Inches(2.2)
    t.columns[1].width = Inches(4.3)
    hdr = t.rows[0]
    hdr.cells[0].merge(hdr.cells[1])
    _set_cell_bg(hdr.cells[0], "1B3A6B")
    hc = hdr.cells[0].paragraphs[0]
    hc.clear()
    hr = hc.add_run("PARENT COMPANY")
    hr.bold = True
    hr.font.size = Pt(11)
    hr.font.color.rgb = WHITE
    hc.alignment = WD_ALIGN_PARAGRAPH.CENTER

    parent_rows = [
        ("Business/ Company Name",    fields.get("parent_name", "")),
        ("Registration Number",       fields.get("parent_reg_no", "")),
        ("Reference No",              fields.get("parent_ref_no", "")),
        ("Registered On",             fields.get("parent_reg_date", "")),
        ("Business Registered Address", fields.get("parent_address", "")),
    ]
    for label, val in parent_rows:
        _add_detail_row(t, label, val)

    # Blank separator row for UK subsidiary
    sep = t.add_row()
    sep.cells[0].merge(sep.cells[1])
    _set_cell_bg(sep.cells[0], "1B3A6B")
    sp = sep.cells[0].paragraphs[0]
    sp.clear()
    sr = sp.add_run("UK SUBSIDIARY")
    sr.bold = True
    sr.font.size = Pt(11)
    sr.font.color.rgb = WHITE
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    uk_rows = [
        ("Business/ Company Name", uk_fields.get("company_name", "")),
        ("Company Number",         uk_fields.get("company_number", "")),
        ("Incorporated On",        uk_fields.get("incorporation_date", "")),
    ]
    for label, val in uk_rows:
        _add_detail_row(t, label, val)

    doc.add_paragraph()
    _body(doc, '(hereinafter referred to as "the Client"),')
    doc.add_paragraph()
    _body(doc, "And")
    doc.add_paragraph()

    # Consultant table (Chisty Law Chambers LLP — fixed)
    t2 = doc.add_table(rows=1, cols=2)
    t2.style = "Table Grid"
    t2.columns[0].width = Inches(2.2)
    t2.columns[1].width = Inches(4.3)
    hdr2 = t2.rows[0]
    hdr2.cells[0].merge(hdr2.cells[1])
    _set_cell_bg(hdr2.cells[0], "1B3A6B")
    hc2 = hdr2.cells[0].paragraphs[0]
    hc2.clear()
    hr2 = hc2.add_run("CONSULTANT")
    hr2.bold = True
    hr2.font.size = Pt(11)
    hr2.font.color.rgb = WHITE
    hc2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    consultant_rows = [
        ("Business/ Company Name",    "CHISTY LAW CHAMBERS LLP"),
        ("Registration Number (SECP)", "0269333"),
        ("Incorporation Date",        "16 September 2024"),
        ("Business Registered Address",
         "2nd floor, Almas Tower, MM Alam Rd, Gulberg II, Lahore, Pakistan."),
    ]
    for label, val in consultant_rows:
        _add_detail_row(t2, label, val)

    doc.add_paragraph()
    _body(doc, '(hereinafter referred to as "the Consultant").')
    doc.add_paragraph()
    _body(doc, 'Collectively referred to as "the Parties".')
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("_______________________________").font.size = Pt(10)
    doc.add_paragraph("Client Signature").runs[0].font.size = Pt(10)
    _body(doc, "OR for and on Behalf of the Client")
    doc.add_paragraph()

    _heading(doc, "Purpose and Engagement")
    _body(doc,
        "This Agreement sets forth the terms under which the Consultant shall provide business "
        "consultancy and structuring guidance to the Client in connection with the compiling, "
        "structure and formatting of their documentation for a Sponsor Licence application under "
        "the UK Expansion Worker route, within the Global Business Mobility visa framework "
        "administered by UK Visas and Immigration (UKVI). The Consultant is not a regulated "
        "immigration adviser under UK law and has not provided services that require regulation "
        "under the UK Immigration and Asylum Act 1999.")
    doc.add_paragraph()

    _heading(doc, "Scope of Services")
    _body(doc, "The Consultant agrees to perform the following services:")
    services = [
        "Provide general procedural guidance on the UK Expansion Worker visa process and compliance requirements.",
        "Organised, formatted, & Compiled a UKVI-compliant business plan for submission to the UK Home Office.",
        "Assist in the organising, formatting and compilation of supporting documentation. Provide strategic recommendations on document structure, formatting, and presentation.",
        "The supporting materials, including the business plan, 12-month financial projection and evidentiary documents, have been prepared and provided by the applicant/client to Chisty Law Chambers LLP.",
    ]
    for s in services:
        _bullet(doc, s)

    doc.add_paragraph()
    _body(doc, "The Consultant has not:")
    exclusions = [
        "Offered legal or immigration advice regulated by UK law.",
        "Submitted or committed to submitting any applications to UKVI or acted as a legal representative.",
        "Represented the Client in dealings with UK authorities.",
    ]
    for e in exclusions:
        _bullet(doc, e)

    doc.add_paragraph()
    _heading(doc, "Disclaimer of Liability")
    _body(doc,
        "The Consultant provides services on a best-efforts basis and does not guarantee any "
        "specific outcome in relation to the Sponsor Licence application. The Client acknowledges "
        "full responsibility for the accuracy and completeness of all submitted documentation.")
    doc.add_paragraph()

    _heading(doc, "Confidentiality")
    _body(doc,
        "Both parties agree to maintain confidentiality regarding all proprietary information "
        "shared during the course of this engagement. This obligation shall survive the "
        "termination of this Agreement.")
    doc.add_paragraph()

    _heading(doc, "Governing Law")
    _body(doc,
        "This Agreement shall be governed by and construed in accordance with the laws of "
        "Pakistan. Any disputes arising from this Agreement shall be resolved through mutual "
        "negotiation, or if necessary, through arbitration.")
    doc.add_paragraph()

    _body(doc, "Signed: ___________________________")
    doc.add_paragraph()
    closing = (
        f"For and on behalf of\n\n"
        f"{fields.get('parent_name', '')} (Pakistan Parent Company) &\n\n"
        f"{uk_fields.get('company_name', '')} (UK Subsidiary)"
    )
    for line in closing.split("\n"):
        lp = doc.add_paragraph(line)
        if lp.runs:
            lp.runs[0].font.size = Pt(10)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

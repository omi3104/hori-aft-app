"""
ANNEX A.1 — Title Pages
Two tables: Parent Company details + UK Subsidiary details
Font: Arial 11pt, spacing after=0 (matches real document)
"""
import io, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Arial"
NAVY = RGBColor(0x1B, 0x3A, 0x6B)

def _to_bytes(doc):
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def _set_doc_font(doc, font_name=FONT):
    doc.styles['Normal'].font.name = font_name

def _p(doc, text="", bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    if text:
        r = p.add_run(text)
        r.font.name = FONT
        r.font.size = Pt(size)
        r.bold = bold
    return p

def _shade_row(row, hex_color="1B3A6B"):
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hex_color)
        tcPr.append(shd)

def _add_table_row(table, label, value, header=False):
    row = table.add_row()
    lc = row.cells[0]
    vc = row.cells[1]
    lp = lc.paragraphs[0]
    vp = vc.paragraphs[0]
    lp.paragraph_format.space_after = Pt(0)
    vp.paragraph_format.space_after = Pt(0)
    lr = lp.add_run(label)
    lr.font.name = FONT
    lr.font.size = Pt(11)
    lr.bold = True
    # Handle multi-line values (e.g. SIC codes joined with \n)
    lines = value.split("\n") if value else [""]
    for i, line in enumerate(lines):
        if i > 0:
            vp.add_run().add_break()
        vr = vp.add_run(line)
        vr.font.name = FONT
        vr.font.size = Pt(11)
        vr.bold = header
    if header:
        _shade_row(row)
        lr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        for r in vp.runs:
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    return row

def generate(fields: dict, uk_fields: dict, output_path):
    doc = Document()
    _set_doc_font(doc)
    for sec in doc.sections:
        sec.top_margin    = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin   = Cm(3)
        sec.right_margin  = Cm(2.5)

    parent_name    = fields.get("parent_name", "")
    parent_reg     = fields.get("parent_reg_no", "")
    parent_ref     = fields.get("parent_ref_no", "")
    parent_date    = fields.get("parent_reg_date", "")
    parent_addr    = fields.get("parent_address", "")
    parent_website   = fields.get("parent_website", "")
    parent_activity  = fields.get("parent_activity", "")
    uk_name          = uk_fields.get("company_name", "")
    uk_num         = uk_fields.get("company_number", "")
    uk_inc         = uk_fields.get("incorporation_date", "")
    uk_addr        = uk_fields.get("registered_address", "")
    uk_sic         = uk_fields.get("sic_codes", [])
    uk_sic_str     = "\n".join(uk_sic) if uk_sic else ""
    psc            = parent_name  # PSC is the parent company

    # ── Intro — each line is its own paragraph (matches real doc) ──
    intro_lines = [
        ("To:", "Sponsor Casework Operations - UK Visa & Immigration"),
        ("Reference / Application:", "Sponsor Licence Application – UK Expansion Worker Route (Global Business Mobility)"),
        ("", "We write in reference to the above."),
        ("", "Please find the full legal status and registration particulars of both entities, "
             "including the parent company's overseas incorporation and the UK subsidiary's "
             "registration with Companies House."),
        ("", "Furthermore, all supporting documentation will be duly attached to verify and "
             "substantiate the contents of this submission, and to address any inadvertent omission "
             "that may arise within this document."),
    ]
    for label, body in intro_lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        if label:
            r1 = p.add_run(label + " ")
            r1.font.name = FONT; r1.font.size = Pt(11); r1.bold = True
        r2 = p.add_run(body)
        r2.font.name = FONT; r2.font.size = Pt(11); r2.bold = True

    _p(doc)

    # ── Parent Company Table ──
    t1 = doc.add_table(rows=0, cols=2)
    t1.style = "Table Grid"
    t1.columns[0].width = Cm(7)
    t1.columns[1].width = Cm(9)

    _add_table_row(t1, "PARENT COMPANY", "DETAILS", header=True)
    parent_rows = [
        ("Business/ Company Name",      parent_name),
        ("Registration Number",         parent_reg),
        ("Reference No",                parent_ref),
        ("Registered On",               parent_date),
        ("Business Registered Address", parent_addr),
        ("Business Trading Address",    parent_addr),
        ("Business Principal Activity", parent_activity),
        ("Business Website",            parent_website),
    ]
    for label, value in parent_rows:
        _add_table_row(t1, label, value)

    _p(doc)

    # ── UK Subsidiary Table ──
    t2 = doc.add_table(rows=0, cols=2)
    t2.style = "Table Grid"
    t2.columns[0].width = Cm(7)
    t2.columns[1].width = Cm(9)

    _add_table_row(t2, "UK SUBSIDAIRY", "DETAILS", header=True)
    uk_rows = [
        ("Business/ Company Name",           uk_name),
        ("Company Number",                   uk_num),
        ("Incorporated On",                  uk_inc),
        ("Registered Office Address",        uk_addr),
        ("Persons with Significant Control (PSC):", psc),
        ("Correspondence Address",           parent_addr),
        ("Nature of business (SIC)",         uk_sic_str),
        ("Business Trading Address",         ""),
    ]
    for label, value in uk_rows:
        _add_table_row(t2, label, value)

    _p(doc)
    _p(doc, "Thank You,", bold=True, size=11)
    _p(doc)
    _p(doc, "For and on behalf of", bold=True, size=11)
    _p(doc, f"{parent_name} (Pakistan Parent Company) &", bold=True, size=11)
    _p(doc, f"{uk_name} (UK Subsidiary)", bold=True, size=11)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

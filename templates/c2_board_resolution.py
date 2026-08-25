"""
ANNEX C.2 — Board Resolution / Minutes of Meeting from the Parent Company
Exact template match.
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


def _set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _heading(doc, text, size=11, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def _body(doc, text, size=10, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    return p


def _bullet(doc, text, size=10):
    p = doc.add_paragraph(style="List Number")
    r = p.add_run(text)
    r.font.size = Pt(size)
    return p


def generate(fields: dict, uk_fields: dict, output_path: str,
             meeting_date: str = "", meeting_time: str = "12:30 PM",
             directors: list = None):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    parent_name = fields.get("parent_name", "")
    parent_reg  = fields.get("parent_reg_no", "")
    parent_ref  = fields.get("parent_ref_no", "")
    parent_addr = fields.get("parent_address", "")
    uk_name     = uk_fields.get("company_name", "")
    uk_num      = uk_fields.get("company_number", "")
    uk_inc      = uk_fields.get("incorporation_date", "")
    ao_name     = fields.get("ao_full_name", "")
    ao_pos      = fields.get("ao_position", "")
    app_date    = meeting_date or fields.get("application_date", "")

    # Attendees — use directors list or fallback to AO only
    attendees = directors or fields.get("parent_directors", [ao_name])
    if not attendees:
        attendees = [ao_name]

    # ── Header block ────────────────────────────────────────────────────────
    _heading(doc, parent_name, size=13)
    doc.add_paragraph()
    _body(doc, f"Company Registration No.: {parent_reg}", size=10)
    _body(doc, f"Company Reference No.: {parent_ref}", size=10)
    _body(doc, f"Registered Address: {parent_addr}", size=10)
    doc.add_paragraph()

    _heading(doc, "BOARD RESOLUTION / MINUTES OF THE MEETING", size=12)
    doc.add_paragraph()

    # Meeting details
    _body(doc, f"Date: {app_date}", size=10)
    _body(doc, f"Time: {meeting_time}", size=10)
    _body(doc, f"Location: {parent_addr}", size=10)
    doc.add_paragraph()
    _body(doc,
        "Agenda: Appointment of Authorising Officer for UK Business Establishment "
        "and Immigration Sponsorship Licence Application.", size=10)
    doc.add_paragraph()

    _heading(doc, "1. Attendance", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc, "The following company officials were present:", size=10)
    for i, name in enumerate(attendees, 1):
        p = doc.add_paragraph(style="List Number")
        p.runs[0].font.size = Pt(10) if p.runs else None
        if not p.runs:
            p.add_run(name).font.size = Pt(10)
        else:
            p.runs[0].text = name

    doc.add_paragraph()
    _heading(doc, "2. Chairperson", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc, f"The meeting was chaired by {ao_name}.", size=10)
    doc.add_paragraph()

    _heading(doc, "3. Purpose of the Meeting", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc,
        "To consider and approve the appointment of an Authorising Officer for the purposes "
        "of establishing the company in the United Kingdom and making an application to the "
        "Home Office for a UK Sponsor Licence under the applicable UK Immigration Rules.", size=10)
    doc.add_paragraph()

    _heading(doc, "4. Discussion", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc,
        "The Chairperson explained the importance of appointing an Authorising Officer, as "
        "required by UK Visas and Immigration (UKVI), to ensure compliance with all sponsorship "
        "obligations, including:", size=10)

    obligations = [
        "Managing the Sponsor Licence Application Process.",
        "Acting as the Main Point of Contact with The Home Office.",
        "Overseeing Immigration Compliance and Record-Keeping Requirements.",
        "Being A Senior and Responsible Person Based Permanently in the UK.",
    ]
    for ob in obligations:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(ob).font.size = Pt(10)

    doc.add_paragraph()
    _body(doc,
        "The board acknowledged that the role carries legal responsibilities and must be "
        "held by a senior, suitable and trusted individual within the company.", size=10)
    doc.add_paragraph()

    _heading(doc, "5. Resolution", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc,
        "After due consideration, based on the education, professional experience and competence, "
        "the board unanimously resolved to appoint:", size=10)
    doc.add_paragraph()
    _body(doc, f"Name: {ao_name}", size=10, bold=True)
    _body(doc, f"Position: {ao_pos}", size=10, bold=True)
    doc.add_paragraph()
    _body(doc,
        f'As the Authorising Officer of the UK subsidiary office with name '
        f'"{uk_name}", which has been incorporated under the Companies Act 2006 in England and Wales, '
        f'for the purposes outlined above, with immediate effect.', size=10)
    doc.add_paragraph()
    _body(doc,
        "The appointed Authorising Officer is authorised and directed to take immediate and all "
        "requisite steps to commence and complete the Sponsor Licence application process.", size=10)
    doc.add_paragraph()
    _body(doc,
        "The Authorising Officer shall also be responsible for ensuring that the company fully "
        "complies with all ongoing duties, responsibilities, and obligations set out in the "
        "UK Visas and Immigration (UKVI) Sponsor Guidance.", size=10)
    doc.add_paragraph()

    _heading(doc, "6. Closing", size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _body(doc,
        "There being no further business, the meeting was concluded.", size=10)
    doc.add_paragraph()

    _body(doc, "Approved by:", size=10)
    doc.add_paragraph()
    _body(doc, "Signed: ___________________________", size=10)
    doc.add_paragraph()
    _body(doc, f"{ao_name} – Chairperson", size=10, bold=True)
    doc.add_paragraph()
    _body(doc, "For and on behalf of", size=10)
    doc.add_paragraph()
    _body(doc, f"{parent_name}", size=10)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

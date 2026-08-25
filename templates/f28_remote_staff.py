"""
ANNEX F.2.8 — Approval of Remote Staff Governance Support
Phase 2 document — requires staff data from org chart / staff list.
Generates: Board Resolution + individual secondment letters for each staff member.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
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


def _heading(doc, text, size=11, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.color.rgb = NAVY
    return p


def _body(doc, text, size=10, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    return p


def _bullet(doc, text, size=10):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    r.font.size = Pt(size)
    return p


def _secondment_letter(doc, ao_name, parent_name, uk_name, board_date, staff_member: dict):
    """Add a secondment letter for one staff member."""
    doc.add_page_break()

    name        = staff_member.get("name", "")
    parent_role = staff_member.get("parent_role", "")
    uk_role     = staff_member.get("uk_role", "")
    hours       = staff_member.get("weekly_hours", 8)
    curr_sal    = staff_member.get("current_salary", "")
    add_pay     = staff_member.get("additional_pay", "")
    total_sal   = staff_member.get("total_salary", "")
    deliverables = staff_member.get("deliverables", [])

    # Get first name for salutation
    first_name = name.split()[-1] if name else name

    _body(doc, f"{name},", size=10, bold=True)
    _body(doc, f"{parent_role}", size=10)
    doc.add_paragraph()
    _body(doc, f"Date: {board_date}", size=10)
    doc.add_paragraph()
    _body(doc,
        f"Ref: Part-Time Secondment Agreement – UK Subsidiary Governance Support "
        f"({hours} Hours Per Week)", size=10, bold=True)
    doc.add_paragraph()
    _body(doc, f"Dear {first_name},", size=10)
    doc.add_paragraph()
    _body(doc,
        f"Further to the Board Resolution passed on {board_date}, we are pleased to confirm "
        f"the terms of your part-time secondment arrangement to provide defined governance "
        f"support to our UK subsidiary, {uk_name}, for a period of 12 months from the "
        f"commencement of UK subsidiary operations.", size=10)
    doc.add_paragraph()
    _body(doc,
        f"This secondment is a formal, structured arrangement. It does not alter your primary "
        f"employment contract with {parent_name} in any respect. Your existing contracted "
        f"working hours, core role, salary from the parent company, leave entitlements, and all "
        f"other employment terms and conditions at {parent_name} remain entirely unchanged and "
        f"continue in full force.", size=10)
    doc.add_paragraph()

    terms = [
        (f"UK Governance Hours:", f"{hours} hours per week, to be completed outside your primary duties at the parent company."),
        ("Scheduling:", "These hours are to be performed in structured weekly sessions, scheduled at times that do not conflict with your core responsibilities. A mutually agreed session schedule will be maintained and made available for audit purposes."),
        ("Mode of Work:", "All UK governance tasks are to be completed remotely, using digital tools and document-sharing systems. No physical presence in the United Kingdom is required or expected."),
        ("Confidentiality & Data Handling:", "All seconded personnel shall maintain confidentiality of UK subsidiary records and comply with internal data protection and document-handling procedures when accessing UK governance documentation remotely."),
        ("Duration:", "12 months from the commencement of UK subsidiary operations, after which the arrangement will be reviewed."),
        ("Operational Boundary:", "During this secondment, you will have no authority to approve payments, enter into contracts, engage with UK clients or regulators directly, or direct UK-based staff. All operational decisions remain the sole responsibility of the Authorising Officer in the United Kingdom."),
    ]
    for label, val in terms:
        p = doc.add_paragraph()
        r1 = p.add_run(label + " ")
        r1.bold = True
        r1.font.size = Pt(10)
        r2 = p.add_run(val)
        r2.font.size = Pt(10)

    doc.add_paragraph()
    _heading(doc, "Seconded UK Governance Role & Defined Deliverables", size=11)
    doc.add_paragraph()
    _body(doc, f"You are seconded to the UK subsidiary in the capacity of {uk_role}.", size=10)
    doc.add_paragraph()

    if deliverables:
        for d in deliverables:
            if isinstance(d, str):
                # May be "Title: Description" format
                if ": " in d:
                    title, desc = d.split(": ", 1)
                    p = doc.add_paragraph()
                    r1 = p.add_run(title + ": ")
                    r1.bold = True
                    r1.font.size = Pt(10)
                    r2 = p.add_run(desc)
                    r2.font.size = Pt(10)
                else:
                    _body(doc, d, size=10)
                doc.add_paragraph()

    if curr_sal or add_pay or total_sal:
        _body(doc,
            f"In recognition of the {hours} hours per week committed to UK governance duties "
            f"under this secondment, your monthly remuneration will be adjusted as follows:",
            size=10)
        doc.add_paragraph()
        for label, val in [
            ("Current Monthly Salary (Parent Company):", curr_sal),
            ("Additional Monthly Remuneration (UK Secondment):", add_pay),
            ("Total Monthly Remuneration:", total_sal),
        ]:
            p = doc.add_paragraph()
            r1 = p.add_run(label + " ")
            r1.bold = True
            r1.font.size = Pt(10)
            r2 = p.add_run(val)
            r2.font.size = Pt(10)
        doc.add_paragraph()
        _body(doc,
            "The additional remuneration reflects the time commitment proportionate to the hours "
            "allocated and will be funded by the UK subsidiary. It does not form part of your "
            "primary employment contract with the parent company and will cease upon conclusion "
            "of the secondment period unless the arrangement is formally renewed.", size=10)

    doc.add_paragraph()
    _body(doc,
        "Please confirm your acceptance of this secondment arrangement by signing and returning "
        "a copy of this letter.", size=10)
    doc.add_paragraph()
    _body(doc, "Thank you for your continued commitment to the organisation.", size=10)
    doc.add_paragraph()
    _body(doc, "Signed (Employer):", size=10)
    doc.add_paragraph()
    _body(doc, "___________________________", size=10)
    _body(doc, f"{ao_name} – Chief Executive Officer", size=10)
    doc.add_paragraph()
    _body(doc, "___________________________", size=10)
    _body(doc, f"{name} – {parent_role}", size=10)


def generate(fields: dict, uk_fields: dict, staff_data: dict, output_path: str):
    """
    staff_data: result from extractor.extract_remote_staff(), containing:
      - staff: list of staff dicts
      - board_date: str
      - total_budget_gbp: str
    """
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
    ao_name     = fields.get("ao_full_name", "")
    ao_pos      = fields.get("ao_position", "")

    staff_list  = staff_data.get("staff", [])
    board_date  = staff_data.get("board_date", fields.get("application_date", ""))
    budget_gbp  = staff_data.get("total_budget_gbp", "£3,000")

    # ── PAGE 1: Board Resolution ─────────────────────────────────────────────
    _heading(doc, parent_name, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()
    _body(doc, f"Company Registration No.: {parent_reg}", size=10)
    _body(doc, f"Company Reference No.: {parent_ref}", size=10)
    doc.add_paragraph()

    _heading(doc, "BOARD RESOLUTION / MINUTES OF THE MEETING",
             size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    _body(doc, f"Date: {board_date}", size=10)
    _body(doc, "Time: 10:00 AM", size=10)
    _body(doc, f"Location: {parent_addr}", size=10)
    doc.add_paragraph()
    _body(doc,
        "Agenda: Approval of Structured Part-Time Secondment of Parent Company Staff for "
        "UK Subsidiary Governance Support.", size=10)
    doc.add_paragraph()

    _heading(doc, "1. Attendance", size=11)
    _body(doc, "The following company officials were present:", size=10)
    for d in fields.get("parent_directors", [ao_name]):
        _bullet(doc, d)
    doc.add_paragraph()

    _heading(doc, "2. Chairperson", size=11)
    _body(doc, f"The meeting was chaired by {ao_name}.", size=10)
    doc.add_paragraph()

    _heading(doc, "3. Purpose of the Meeting", size=11)
    _body(doc,
        f"To consider and formally approve a structured, part-time secondment arrangement for "
        f"parent company staff members, enabling them to provide defined governance and advisory "
        f"support to the UK subsidiary, {uk_name}, during its initial establishment period.",
        size=10)
    doc.add_paragraph()

    if staff_list:
        _body(doc,
            "The Chairperson presented a workload capacity review for each of the proposed seconded "
            "staff members. The following persons were approved to be part of the secondment "
            "governance team:", size=10)
        doc.add_paragraph()
        for s in staff_list:
            _bullet(doc, f"{s.get('name', '')} ({s.get('parent_role', '')}, Parent Company)")

    doc.add_paragraph()
    _body(doc,
        "The board satisfied itself that in each case the weekly allocation is operationally "
        "feasible, does not reduce productivity at the parent company, and is supported by the "
        "nature of each role's workflow. The board further noted that the UK governance tasks "
        "assigned to each individual are strictly non-operational and do not require the "
        "individuals to be physically present in the United Kingdom.", size=10)
    doc.add_paragraph()
    _body(doc,
        "It was confirmed and recorded that the secondment arrangement is time-bound to the "
        "first 12 months of UK subsidiary operations, after which the board will review whether "
        "continued support is required.", size=10)
    doc.add_paragraph()

    _heading(doc, "4. Resolution", size=11)
    _body(doc,
        "After due consideration of the capacity review and the operational boundaries described "
        "above, the board unanimously resolved to approve a formal part-time secondment of the "
        "following parent company staff members:", size=10)
    doc.add_paragraph()

    for s in staff_list:
        _body(doc, f"Name: {s.get('name', '')}", size=10, bold=True)
        _body(doc, f"Current Role in Parent Company: {s.get('parent_role', '')}", size=10)
        _body(doc, f"Seconded UK Governance Role: {s.get('uk_role', '')}", size=10)
        _body(doc, f"Weekly Time Allocation for UK Duties: {s.get('weekly_hours', 8)} hours per week", size=10)
        _body(doc, "Secondment Duration: 12 months from the commencement of UK subsidiary operations", size=10)
        doc.add_paragraph()

    if budget_gbp:
        _body(doc,
            f"For this purpose, {budget_gbp} has been allocated within the UK Establishment's "
            f"capital to accommodate the supporting staff, in addition to their remuneration "
            f"already receiving from the parent company.", size=10)

    doc.add_paragraph()
    _heading(doc, "5. Closing", size=11)
    _body(doc,
        "There being no further business, the meeting was concluded.", size=10)
    doc.add_paragraph()
    _body(doc, "Signed: ___________________________", size=10)
    doc.add_paragraph()
    _body(doc, f"{ao_name} – Chairperson", size=10, bold=True)
    doc.add_paragraph()
    _body(doc, "For and on behalf of", size=10)
    _body(doc, f"{parent_name}", size=10)

    # ── Individual secondment letters ────────────────────────────────────────
    for s in staff_list:
        _secondment_letter(doc, ao_name, parent_name, uk_name, board_date, s)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

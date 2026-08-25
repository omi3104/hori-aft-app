"""
ANNEX C.8 — Statement of Truth by the Authorising Officer
Font: Arial 11pt, 1.5x line spacing (matches real document)
"""
import io, os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT = "Arial"

def _to_bytes(doc):
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def _set_doc_font(doc):
    doc.styles['Normal'].font.name = FONT

def _p(doc, text="", bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    if text:
        r = p.add_run(text)
        r.font.name = FONT
        r.font.size = Pt(size)
        r.bold = bold
    return p

def generate(fields: dict, uk_fields: dict, output_path, doc_date: str = ""):
    doc = Document()
    _set_doc_font(doc)
    for sec in doc.sections:
        sec.top_margin    = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin   = Cm(3)
        sec.right_margin  = Cm(2.5)

    parent_name  = fields.get("parent_name", "")
    parent_addr  = fields.get("parent_address", "")
    uk_name      = uk_fields.get("company_name", "")
    uk_addr      = uk_fields.get("registered_address", "")
    ao_name      = fields.get("ao_full_name", "")
    ao_dob       = fields.get("ao_dob", "")
    ao_pp        = fields.get("ao_passport", "")
    ao_nat       = fields.get("ao_nationality", "Pakistan")
    date_signed  = doc_date or fields.get("application_date", "")

    # ── Title ──
    _p(doc, "STATEMENT OF TRUTH", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    _p(doc, "BY THE AUTHORISING OFFICER", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    _p(doc, "Reference: Sponsor Licence Application – UK Expansion Worker Route (Global Business Mobility)", bold=True, size=11, space_after=6)
    _p(doc)

    _p(doc, "Business Name:", bold=True, size=11)
    _p(doc, f"{parent_name}     Address: {parent_addr}", size=11)
    _p(doc)
    _p(doc, f"{uk_name} (Subsidiary Registered Office) Address: {uk_addr}", size=11)
    _p(doc)

    _p(doc,
       f"Applicant (Authorising Officer): {ao_name}, D.O.B: {ao_dob}, "
       f"Passport Number {ao_pp}, {ao_nat}.",
       bold=True, size=11)
    _p(doc)

    _p(doc,
       f"I, {ao_name}, hereby make the following statement in connection with the above-mentioned "
       f"Sponsor Licence application and do so truthfully and on behalf of {parent_name}.",
       size=11)
    _p(doc)

    # Numbered paragraphs
    items = [
        f"I am currently employed by {parent_name} and have been continuously employed by the "
        f"company for a period exceeding twelve (12) months prior to the date of this statement.",

        f"I have been formally appointed as the Authorising Officer for the proposed establishment "
        f"of the UK subsidiary of {parent_name}. This subsidiary has been incorporated under the "
        f"laws of England and Wales in accordance with section 1159 of the Companies Act 2006, as "
        f"a wholly owned subsidiary of our overseas parent company based in Pakistan.",

        f"{parent_name} has engaged the services of Chisty Law Chambers LLP (Incorporation No. 0269333), "
        f"a legal consultancy firm based in Pakistan, for the purposes of providing general advisory "
        f"support in relation to the Sponsor Licence application. Their principal business place is "
        f"located at: 2nd Floor, Almas Tower, MM Alam Road, Gulberg II, Lahore, Pakistan.",

        "The scope of services provided by Chisty Law Chambers LLP is strictly limited to general "
        "advisory, compilation, and procedural assistance in connection with the preparation of the "
        "company's business documentation. This includes, without limitation, the Business Plan, "
        "twelve-month financial projections, and the Sponsorship Licence application.\n\n"
        "For the avoidance of doubt, the firm 'Chisty Law Chambers LLP' does not assume "
        "responsibility for the accuracy, completeness, or substantive content of any such "
        "documentation, which remains the sole responsibility of the authorising officer (me) "
        "and/or the company.",

        "Chisty Law Chambers LLP has not been appointed to act as our legal representative for "
        "the purposes of this application, nor are they authorised to submit the application to "
        "the UKVI on my behalf or on behalf of the company.",

        "I hereby acknowledge and confirm that I, and the company which I represent, bear full "
        "and continuing responsibility for the accuracy, completeness, and truthfulness of all "
        "information and documentation submitted in connection with the UK Expansion Worker Visa "
        "Sponsorship Licence Application.",

        "This responsibility expressly includes, without limitation, all business and personal "
        "documentation supplied by or on behalf of the company or myself, including (but not "
        "limited to) the Business Plan, 12-month financial projections, and any and all supporting "
        "materials provided in support of the application.",

        "I further acknowledge that such information and documentation have been prepared and "
        "provided under my instruction and authority.",

        "I further confirm that the contents of this statement are true to the best of my "
        "knowledge and belief.",
    ]

    for item in items:
        np = doc.add_paragraph(style="List Number")
        np.paragraph_format.space_after = Pt(6)
        np.paragraph_format.line_spacing = 1.5
        r = np.add_run(item)
        r.font.name = FONT
        r.font.size = Pt(11)

    _p(doc)
    _p(doc, "Thank You,", size=11)
    _p(doc)
    _p(doc)
    _p(doc, "Signed: ___________________________", size=11)
    _p(doc, f"Mr./Ms. {ao_name} – Authorising Officer", size=11)
    _p(doc)
    _p(doc, "For and on behalf of", size=11)
    _p(doc, f"{parent_name} (Pakistan Parent Company) &", size=11)
    _p(doc, f"{uk_name} (UK Subsidiary)", size=11)
    _p(doc)
    _p(doc, f"Date: {date_signed}", size=11)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

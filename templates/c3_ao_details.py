"""
ANNEX C.3 — AO Details
Letter to Sponsor Casework Operations (Home Office) about the Authorising Officer job role.
Font: Arial 11pt, space_after=0 (matches real document)
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

    parent_name   = fields.get("parent_name", "")
    uk_name       = uk_fields.get("company_name", "")
    ao_name       = fields.get("ao_full_name", "")
    ao_dob        = fields.get("ao_dob", "")
    ao_pp         = fields.get("ao_passport", "")
    ao_nat        = fields.get("ao_nationality", "Pakistan")
    ao_pos        = fields.get("ao_position", "")
    ao_uk_title   = fields.get("ao_uk_title", "Executive Director")
    soc_code      = fields.get("ao_soc_code", "1111")
    going_rate    = fields.get("ao_going_rate", "£60,000")
    going_hourly  = fields.get("ao_going_rate_hourly", "£30.77 per hour")
    directors     = fields.get("parent_directors", [])
    reporting_to  = fields.get("reporting_to", "")
    letter_date   = doc_date or fields.get("application_date", "")

    # Signatory
    signatory = next((d for d in directors if d.strip().lower() != ao_name.strip().lower()), "")
    if not signatory and directors:
        signatory = directors[-1]

    # ── Address block ──
    _p(doc, "To:", size=11)
    _p(doc, "Sponsor Casework Operations", bold=True, size=11)
    _p(doc, "Vulcan House - Steel", size=11)
    _p(doc, "PO Box 3468", size=11)
    _p(doc, "Sheffield S3 8WA, United Kingdom", size=11)
    _p(doc)

    if letter_date:
        _p(doc, f"Date: {letter_date}", size=11)
        _p(doc)

    _p(doc, "Dear Sirs:", size=11)
    _p(doc)

    _p(doc,
       "Ref: Details of Identified Authorising Officer for Subsidiary Office – "
       "UK Expansion Worker Route (Global Business Mobility)",
       bold=True, size=11)
    _p(doc)

    _p(doc,
       f"Applicant (Authorising Officer): {ao_name}, D.O.B: {ao_dob}, "
       f"Passport Number {ao_pp}, {ao_nat}.",
       size=11)
    _p(doc)

    _p(doc,
       "We write in reference to the above. Please see below the details of the required "
       "job role for our Authorising Officer.", size=11)
    _p(doc)

    _p(doc,
       "The details are being provided in accordance with the requirements mentioned in "
       "paragraph 3.10 of Appendix A-Supporting Documents for Sponsor Licence.", size=11)
    _p(doc)

    _p(doc,
       "Paragraph 3.10. UK Expansion Worker (Global Business Mobility) at:\n"
       "https://assets.publishing.service.gov.uk/media/67f3de36c2fea2548f4eff19/"
       "Sponsor-guidance-Appendix-A-supporting-documents-04-25-v1.0.pdf",
       size=10)
    _p(doc)

    _p(doc, "We are requesting the following job role for our Authorising Officer:", size=11)
    _p(doc)

    _p(doc, f"Job Title:    {ao_uk_title}", size=11)
    _p(doc, "Job Type:     Chief executives and senior officials", size=11)
    _p(doc, f"SOC Code:     {soc_code}", size=11)
    _p(doc, f"Going Rate:   {going_rate} ({going_hourly})", size=11)
    _p(doc)

    _p(doc, "The Authorising Officer/Worker has been identified considering:", size=11)

    criteria = [
        "The seniority and important role in the overseas business",
        "The area of operations in the overseas business",
        "The knowledge of relevant industry and services",
        "The proposed operations of the UK entity and relevance of the worker",
    ]
    for c in criteria:
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(c)
        r.font.name = FONT
        r.font.size = Pt(11)

    _p(doc)

    _p(doc,
       f"Moreover, Subject to grant of sponsor license and immigration permission to "
       f"Mr. {ao_name}, he will travel to the United Kingdom to undertake the assignment "
       f"of expansion.", size=11)
    _p(doc)

    # Reporting line
    if reporting_to:
        _p(doc,
           f"The {reporting_to} will be responsible to run the business operations after "
           f"acquiring designated authorisations from the {ao_pos or 'senior officer'}. "
           f"The course of action related to executive powers including financial mandates, "
           f"and limitations will be decided once the license application is approved.", size=11)
    else:
        _p(doc,
           "The Manager Operations will be responsible to run the business operations after "
           "acquiring designated authorisations from the Chief Executive Officer. The course of "
           "action related to executive powers including financial mandates, and limitations will "
           "be decided once the license application is approved.", size=11)

    _p(doc)

    _p(doc,
       "We believe that our Sponsor Licence Application fulfils all the requirements and is "
       "presented in a manner consistent with the standards and expectations relevant to "
       "establishing a subsidiary office in the United Kingdom.", size=11)
    _p(doc)

    _p(doc,
       "However, should you have any further queries or require clarification or additional "
       "supporting documentation in relation to our application, please do not hesitate to "
       "contact us.", size=11)
    _p(doc)

    _p(doc, "Thank You,", size=11)
    _p(doc)
    _p(doc)
    _p(doc, "Signed: ___________________________", size=11)
    _p(doc)
    if signatory:
        _p(doc, signatory, size=11)
    _p(doc, "For and on behalf of", size=11)
    _p(doc, f"{parent_name} (Pakistan Parent Company) &", size=11)
    _p(doc, f"{uk_name} (UK Subsidiary)", size=11)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

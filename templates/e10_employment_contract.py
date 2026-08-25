"""
ANNEX E.12 — Employment Contract (Draft Copy)
UK Employment Agreement for the Expansion Worker
Font: Arial 11pt, single line spacing (matches real document)
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

def _p(doc, text="", bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6):
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

def _clause(doc, number, title, body_paras):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{number}. {title}")
    r.font.name = FONT
    r.bold = True
    r.font.size = Pt(11)
    for b in body_paras:
        bp = doc.add_paragraph()
        bp.paragraph_format.space_after = Pt(4)
        bp.paragraph_format.space_before = Pt(0)
        r = bp.add_run(b)
        r.font.name = FONT
        r.font.size = Pt(11)

def generate(fields: dict, uk_fields: dict, output_path,
             salary: str = "", start_date: str = ""):
    doc = Document()
    _set_doc_font(doc)
    for sec in doc.sections:
        sec.top_margin    = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin   = Cm(3)
        sec.right_margin  = Cm(2.5)

    parent_name  = fields.get("parent_name", "")
    uk_name      = uk_fields.get("company_name", "")
    uk_addr      = uk_fields.get("registered_address", "")
    uk_num       = uk_fields.get("company_number", "")
    ao_name      = fields.get("ao_full_name", "")
    ao_dob       = fields.get("ao_dob", "")
    ao_pp        = fields.get("ao_passport", "")
    ao_nat       = fields.get("ao_nationality", "Pakistan")
    ao_uk_title  = fields.get("ao_uk_title", "Executive Director")
    soc_code     = fields.get("ao_soc_code", "1111")
    going_rate   = salary or fields.get("ao_going_rate", "£60,000")
    job_duties   = fields.get("job_duties", [])
    start        = start_date or "[Insert Date]"

    # ── Title ──
    _p(doc, "Employment Agreement", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    intro = doc.add_paragraph()
    intro.paragraph_format.space_after = Pt(6)
    intro.paragraph_format.space_before = Pt(0)
    r1 = intro.add_run("This Employment Agreement")
    r1.font.name = FONT; r1.bold = True; r1.font.size = Pt(11)
    r2 = intro.add_run(f" is made on {start} between:")
    r2.font.name = FONT; r2.font.size = Pt(11)
    _p(doc)

    _p(doc,
       f"Employer: {uk_name}: Registered Office: {uk_addr} "
       f"Company Number: {uk_num} (the \"Employer\" or \"Company\") "
       f"(Registered Subsidiary of {parent_name}, a Company registered in Pakistan)",
       bold=True, size=11)
    _p(doc)
    _p(doc, "And", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc)
    _p(doc,
       f"Employee: {ao_name}, D.O.B: {ao_dob}, Passport Number {ao_pp}, {ao_nat} "
       f"(the \"Employee\")",
       bold=True, size=11)
    _p(doc)

    # Clause 1
    _clause(doc, "1", "Commencement and Duration", [
        f"The Employee's employment under this Agreement shall commence on {start} and shall "
        f"continue until one year from Commencement Date, unless terminated earlier in accordance "
        f"with the provisions of this Agreement.",
        "The Employee's employment is subject to the Employee obtaining and maintaining a valid UK "
        "Expansion Worker visa under the Global Business Mobility: Expansion Worker immigration route, "
        "sponsored by the Employer. The Employee agrees to provide all necessary documentation and "
        "cooperate fully in the visa application and maintenance process.",
        "This Agreement constitutes a fixed-term contract for the purposes of the Employer's "
        "sponsorship obligations under the UK Immigration Rules.",
    ])

    # Clause 2
    duties_text = (
        "\n".join(f"- {d}" for d in job_duties)
        if job_duties else
        "establish and manage the UK branch operations, including market entry strategies, sales, "
        "and compliance with the proposed business plan in accordance with UK regulations."
    )
    _clause(doc, "2", "Job Title & Duties", [
        f"The Employee shall be employed as {ao_uk_title}, which corresponds to the Standard "
        f"Occupational Classification (SOC) 2020 occupation code {soc_code} as specified on the "
        f"Certificate of Sponsorship (CoS) issued by the Employer.",
        f"The Employee's principal duties shall be to {duties_text}",
    ])

    # Clause 3
    _clause(doc, "3", "Place of Work", [
        f"The Employee's principal place of work shall be {uk_addr} and/or such other location in "
        f"the UK as the Employer may reasonably require.",
        "The Employee may be required to travel within the UK or overseas as necessary for the "
        "performance of their duties, with reasonable expenses reimbursed in accordance with the "
        "Employer's policies.",
    ])

    # Clause 4
    _clause(doc, "4", "Remuneration", [
        f"The Employee shall be paid a gross annual salary of {going_rate} payable in monthly "
        f"instalments in arrears by bank transfer or any other banking transaction modes on or "
        f"before 5th working day of every month.",
        "The Salary is inclusive of all allowances unless specified otherwise.",
        "The Salary shall be subject to deductions for tax, National Insurance contributions, and "
        "any other statutory deductions. The Employee will be paid through the Employer's PAYE scheme.",
        "The Employer confirms that the remuneration complies with the National Minimum Wage Act 1998 "
        "and meets or exceeds the minimum salary threshold for the UK Expansion Worker route.",
    ])

    # Clause 5
    _clause(doc, "5", "Hours of Work", [
        "The Employee's normal working hours shall be 37.5 hours per week, Monday to Friday, "
        "9:00 am to 5:30 pm, exclusive of lunch breaks.",
    ])

    # Clause 6
    _clause(doc, "6", "Holiday Entitlement", [
        "The Employee is entitled to 28 days paid annual leave per holiday year, including public holidays.",
        "Holiday must be taken at times approved by the Employer and may not be carried forward without prior agreement.",
    ])

    # Clause 7
    _clause(doc, "7", "Pension and Benefits", [
        "The Employer shall enroll the Employee in its auto-enrolment pension scheme in accordance "
        "with the Pensions Act 2008.",
    ])

    # Clause 8
    _clause(doc, "8", "Sponsorship and Immigration Obligations", [
        "The Employee acknowledges that their employment is conditional upon the Employer holding a "
        "valid Sponsor Licence and issuing a valid CoS for the UK Expansion Worker route.",
        "The Employee shall: work only for the Employer in the role specified on the CoS; not engage "
        "in supplementary employment except as permitted under the Immigration Rules; not access public "
        "funds; promptly notify the Employer of any changes in personal circumstances that may affect "
        "their visa status; apply for visa extensions or changes as directed by the Employer.",
        "If the Employee's visa or sponsorship is revoked or expires without renewal, the employment "
        "shall terminate automatically.",
        "The Employer may terminate this Agreement immediately without notice if the Employee breaches "
        "immigration conditions or if the Sponsor's licence is downgraded, curtailed, or revoked.",
    ])

    # Clause 9
    _clause(doc, "9", "Confidentiality and Intellectual Property", [
        "The Employee shall keep confidential all information relating to the Employer's business and "
        "shall not use or disclose it except as required for their duties.",
        "All intellectual property created by the Employee during employment shall belong to the Employer.",
    ])

    # Clause 10
    _clause(doc, "10", "Termination", [
        "Either party may terminate this Agreement by 28 days written notice during the Employment Period.",
        "The Employer may terminate summarily for gross misconduct.",
        "Upon termination, the Employee shall return all company property and comply with garden leave "
        "provisions if applicable.",
    ])

    # Clause 11
    _clause(doc, "11", "Data Protection", [
        "The parties agree to comply with the UK GDPR and Data Protection Act 2018. The Employee "
        "consents to the processing of their personal data for employment and immigration purposes.",
    ])

    # Clause 12
    _clause(doc, "12", "Governing Law and Jurisdiction", [
        "This Agreement shall be governed by the laws of England and Wales. The parties submit to "
        "the exclusive jurisdiction of the courts of England and Wales.",
    ])

    _p(doc)
    _p(doc, "Execution", bold=True, size=11)
    _p(doc)
    _p(doc, "Signed by the Employee: ___________________________", bold=True, size=11)
    _p(doc, "Date: ___________", bold=True, size=11)
    _p(doc)
    _p(doc, "Signed for and on behalf of the Employer: ___________________________", bold=True, size=11)
    _p(doc, "Date: ___________", bold=True, size=11)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

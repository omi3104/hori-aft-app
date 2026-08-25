"""
ANNEX B.1 — Consultancy Agreement between the Business & Chisty Law Chambers LLP
"""
import io, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1B, 0x3A, 0x6B)

def _to_bytes(doc):
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def _p(doc, text="", bold=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    if text:
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
    return p

def _section(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = NAVY
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
    lp = row.cells[0].paragraphs[0]
    vp = row.cells[1].paragraphs[0]
    lr = lp.add_run(label)
    vr = vp.add_run(value)
    lr.font.size = Pt(10); lr.bold = True
    vr.font.size = Pt(10); vr.bold = True
    if header:
        _shade_row(row)
        lr.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        vr.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)

def generate(fields: dict, uk_fields: dict, output_path, agreement_date: str = ""):
    doc = Document()
    for sec in doc.sections:
        sec.top_margin    = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin   = Cm(3)
        sec.right_margin  = Cm(2.5)

    parent_name  = fields.get("parent_name", "")
    parent_reg   = fields.get("parent_reg_no", "")
    parent_ref   = fields.get("parent_ref_no", "")
    parent_date  = fields.get("parent_reg_date", "")
    parent_addr  = fields.get("parent_address", "")
    uk_name      = uk_fields.get("company_name", "")
    uk_num       = uk_fields.get("company_number", "")
    uk_inc       = uk_fields.get("incorporation_date", "")
    agr_date     = agreement_date or fields.get("application_date", "")

    # Title
    _p(doc, "CONSULTANCY AGREEMENT", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    _p(doc, f"This Agreement is made on the {agr_date}, by and between:", size=11)
    _p(doc)

    # Client table
    t1 = doc.add_table(rows=0, cols=2)
    t1.style = "Table Grid"
    t1.columns[0].width = Cm(7)
    t1.columns[1].width = Cm(9)
    _add_table_row(t1, "PARENT COMPANY",       "DETAILS",    header=True)
    _add_table_row(t1, "Business/ Company Name", parent_name)
    _add_table_row(t1, "Registration Number",   parent_reg)
    _add_table_row(t1, "Reference No",          parent_ref)
    _add_table_row(t1, "Registered On",         parent_date)
    _add_table_row(t1, "Business Registered Address", parent_addr)
    _add_table_row(t1, "UK SUBSIDIARY",         "DETAILS",   header=True)
    _add_table_row(t1, "Business/ Company Name", uk_name)
    _add_table_row(t1, "Company Number",        uk_num)
    _add_table_row(t1, "Incorporated On",       uk_inc)

    _p(doc, "(hereinafter referred to as \"the Client\"),", size=11)
    _p(doc)
    _p(doc, "And", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc)

    # Consultant table
    t2 = doc.add_table(rows=0, cols=2)
    t2.style = "Table Grid"
    t2.columns[0].width = Cm(7)
    t2.columns[1].width = Cm(9)
    _add_table_row(t2, "Business/ Company Name",    "CHISTY LAW CHAMBERS LLP",          header=False)
    _add_table_row(t2, "Registration Number (SECP)\nIncorporation Date", "0269333\n16 September 2024")
    _add_table_row(t2, "Business Registered Address", "2nd floor, Almas Tower, MM Alam Rd, Gulberg II, Lahore, Pakistan.")

    _p(doc, "(hereinafter referred to as \"the Consultant\").", size=11)
    _p(doc)
    _p(doc, "Collectively referred to as \"the Parties\".", bold=True, size=11)
    _p(doc)
    _p(doc, "___________________________________", size=11)
    _p(doc, "Client Signature", size=10)
    _p(doc, "OR for and on Behalf of the Client", size=10)
    _p(doc)

    # Sections
    _section(doc, "Purpose and Engagement")
    _p(doc,
       "This Agreement sets forth the terms under which the Consultant shall provide business "
       "consultancy and structuring guidance to the Client in connection with the compiling, "
       "structure and formatting of their documentation for a Sponsor Licence application under "
       "the UK Expansion Worker route, within the Global Business Mobility visa framework "
       "administered by UK Visas and Immigration (UKVI). The Consultant is not a regulated "
       "immigration adviser under UK law and has not provided services that require regulation "
       "under the UK Immigration and Asylum Act 1999.", size=11)

    _section(doc, "Scope of Services")
    _p(doc, "The Consultant agrees to perform the following services:", size=11)
    services = [
        "Provide general procedural guidance on the UK Expansion Worker visa process and compliance requirements.",
        "Organised, formatted, & Compiled a UKVI-compliant business plan for submission to the UK Home Office.",
        "Assist in the organising, formatting and compilation of supporting documentation. Provide strategic recommendations on document structure, formatting, and presentation.",
        "The supporting materials, including the business plan, 12-month financial projection and evidentiary documents, have been prepared and provided by the applicant/client to Chisty Law Chambers LLP.",
    ]
    for s in services:
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(2)
        bp.add_run(s).font.size = Pt(11)
    _p(doc)
    _p(doc, "The Consultant has not:", bold=True, size=11)
    not_services = [
        "Offer legal or immigration advice regulated by UK law.",
        "Submit or commit to submitting any applications to UKVI or act as a legal representative.",
        "Represent the Client in dealings with UK authorities.",
        "Guarantee the outcome of any immigration or sponsor licence application.",
    ]
    for s in not_services:
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(2)
        bp.add_run(s).font.size = Pt(11)
    _p(doc)
    _p(doc,
       "The Client accepts complete and sole responsibility for the accuracy, completeness, and "
       "content of all documentation and representations submitted in connection with their UK "
       "Expansion Worker Visa Sponsor Licence application. This includes, without limitation, the "
       "Business Plan, twelve-month financial projections, and any related materials, as well as "
       "responsibility for submitting such documentation to the relevant authorities.", size=11)

    _section(doc, "Legal Status and Regulatory Clarification")
    _p(doc,
       "The Consultant confirms that it operates under the jurisdiction of Pakistan and is not "
       "regulated by the UK Office of the Immigration Advice Authority Services Commissioner "
       "(OISC), which is now called the Immigration Advice Authority. This Agreement reflects a "
       "business consultancy engagement and does not constitute legal representation within the "
       "meaning of UK law.", size=11)
    _p(doc)
    _p(doc, "___________________________________", size=11)
    _p(doc, "Client Signature", size=10)
    _p(doc, "OR for and on Behalf of the Client", size=10)

    _section(doc, "Fees and Payment Terms")
    _p(doc,
       "The Client agrees to pay a non-refundable total consultancy fee to the Consultant for the "
       "services described in this agreement. Payments shall be made in accordance with the following schedule:", size=11)
    _p(doc)
    _p(doc, "Total Amount: PKR 300,000. (Three Hundred Thousand Pakistani Rupees)", size=11)
    _p(doc)
    fee_items = [
        "First Payment: 50% on signing of this agreement. PKR 150,000. (One Hundred and Fifty Thousand Pakistani Rupees)",
        "Second Payment: Remaining 50% of the total amount agreed. After providing all the services under this agreement, PKR 150,000. (One Hundred and Fifty Thousand Pakistani Rupees)",
    ]
    for f in fee_items:
        bp = doc.add_paragraph(style="List Bullet")
        bp.add_run(f).font.size = Pt(11)

    _section(doc, "5. Confidentiality")
    _p(doc,
       "Both Parties agree to maintain the confidentiality of any documentation or personal data "
       "exchanged under this Agreement, except where disclosure is required by law.", size=11)

    _section(doc, "6. Limitation of Liability")
    _p(doc,
       "The Consultant shall not be liable for the rejection, delay, or adverse outcome of any "
       "application submitted by the Client. The Client acknowledges and accepts that the final "
       "responsibility for the application's content, accuracy, and submission rests solely with them.", size=11)

    _section(doc, "7. Term and Termination")
    _p(doc,
       "This Agreement shall remain in effect until the completion of services or until terminated "
       "by either Party with 30 (Thirty) days' written notice.", size=11)

    _section(doc, "8. Governing Law and Jurisdiction")
    _p(doc,
       "This Agreement shall be governed by the laws of Pakistan. Any disputes arising from or in "
       "connection with this Agreement shall be subject to the exclusive jurisdiction of the courts of Pakistan.", size=11)

    _section(doc, "9. Force Majeure & Dispute Settlement")
    _p(doc,
       "Neither party shall be under any obligation to the other if performance is rendered impossible "
       "due to an event of force majeure, being an event, which is beyond the control of either of the "
       "parties, such as Natural disaster, floods, war, epidemics, etc.", size=11)

    _section(doc, "10. Entire Agreement")
    _p(doc,
       "This Agreement constitutes the entire understanding between the Parties and supersedes all "
       "previous oral or written communications relating to the subject matter.", size=11)

    _p(doc)
    _p(doc, "IN WITNESS WHEREOF, the Parties hereto have executed this Agreement as of the date first written above.", size=11)
    _p(doc)
    _p(doc, "___________________________________", size=11)
    _p(doc, "'The Client',", bold=True, size=11)
    _p(doc, "For and on behalf of", size=11)
    _p(doc, parent_name, bold=True, size=11)
    _p(doc)
    _p(doc, "___________________________________", size=11)
    _p(doc, "'The Consultant',", bold=True, size=11)
    _p(doc, "For and on behalf of", size=11)
    _p(doc, "CHISTY LAW CHAMBERS LLP", bold=True, size=11)
    _p(doc, "(0269333)", size=11)

    if output_path is None:
        return _to_bytes(doc)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

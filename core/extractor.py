"""extractor.py — Groq AI extraction. Reads GROQ_API_KEY from environment."""
import os, json, re
from groq import Groq

EXTRACTION_PROMPT = """
You are a document analysis assistant. Extract the following from the document text and return ONLY valid JSON — no markdown, no explanation.

{
  "parent_name": "",
  "parent_secp_uin": "",
  "parent_incorp_date": "",
  "parent_reg_no": "",
  "parent_ref_no": "",
  "parent_reg_date": "",
  "parent_address": "",
  "parent_trading_address": "",
  "parent_directors": [],
  "ao_full_name": "",
  "ao_dob": "",
  "ao_passport": "",
  "ao_nationality": "",
  "ao_position": "",
  "ao_email": "",
  "ao_uk_title": "",
  "ao_uk_job_type": "",
  "ao_soc_code": "",
  "ao_going_rate": "",
  "ao_going_rate_hourly": "",
  "application_date": "",
  "job_description": "",
  "job_duties": [],
  "reporting_to": "",
  "department": "",
  "parent_website": "",
  "parent_email": "",
  "parent_activity": "",
  "company_type": "",
  "board_attendees": []
}

Rules:
- parent_name: full business/company name (e.g. M/S AL-HABIB ENGINEERING & CONTRACTOR)
- parent_secp_uin: SECP Corporate Universal Identification No. (CUIN) — 7-digit number, if the company is SECP-registered
- parent_incorp_date: SECP date of incorporation, formatted as DD Month YYYY (may differ from FBR registration date)
- parent_reg_no: FBR/SECP/CTRN registration number
- parent_ref_no: FBR reference number if shown
- parent_reg_date: FBR registration date, formatted as DD Month YYYY
- parent_trading_address: business trading address if it differs from the registered address; else leave ""
- parent_directors: list of director/owner/partner full names
- ao_email: the Authorising Officer's email address if shown in any document
- parent_email: the parent company's general/official email address if shown
- ao_uk_title: proposed UK job title (default "Executive Director" if unclear)
- ao_uk_job_type: the SOC occupation group label for the job title (e.g. "Chief executives and senior officials", "Marketing, sales and advertising directors")
- ao_soc_code: SOC 2020 code (default "1111" if unclear)
- ao_going_rate: annual salary e.g. "£60,000"
- ao_going_rate_hourly: e.g. "£30.77 per hour"
- job_description: a one paragraph summary of the role purpose and responsibilities (extract from Business Profile or CV if present)
- job_duties: list of key duties/responsibilities as bullet points (extract from Business Profile or Job Description section in any document)
- reporting_to: who the employee reports to (from org chart or CV)
- department: department or division name (from business profile or org chart)
- parent_website: company website URL if mentioned in any document
- parent_activity: business principal activity / SIC code description from SECP/FBR registration (e.g. "890173 – Other Service Activities / Services / Contractor")
- company_type: legal entity type — one of: "Sole Proprietorship", "Association of Persons", "Private Limited", "Partnership", "Public Limited" — infer from documents
- board_attendees: list of senior management with designations from hierarchy/org chart — format each as "Full Name, Designation" (e.g. "Muhammad Usman, Chief Executive Officer"). Include AO plus other senior managers. If no org chart provided, leave as empty list.
- Files prefixed [OPTIONAL] are supplementary — prioritise them for job_description, job_duties, reporting_to, department, board_attendees, parent_website
- Return "" or [] for any field not found
"""

STAFF_PROMPT = """
Extract remote/seconded staff information from the document and return ONLY valid JSON:

{
  "staff": [
    {
      "name": "",
      "parent_role": "",
      "uk_role": "",
      "weekly_hours": 8,
      "current_salary": "",
      "additional_pay": "",
      "total_salary": "",
      "deliverables": ["", "", ""]
    }
  ],
  "board_date": "",
  "total_budget_gbp": ""
}
"""

def _repair_json(raw: str) -> str:
    """Attempt to close a truncated JSON object by appending missing closing chars."""
    # Count open braces/brackets to determine what needs closing
    stack = []
    in_str = False
    escape = False
    for ch in raw:
        if escape:
            escape = False
            continue
        if ch == '\\' and in_str:
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in '{[':
            stack.append('}' if ch == '{' else ']')
        elif ch in '}]':
            if stack:
                stack.pop()
    # Close any open string, then close remaining structures
    closing = ''
    if in_str:
        closing += '"'
    closing += ''.join(reversed(stack))
    return raw.rstrip() + closing

def _parse(raw: str) -> dict:
    # Strip thinking tags from reasoning models
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw)
    # Try as-is
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try extracting outermost {...}
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        fragment = m.group()
        try:
            return json.loads(fragment)
        except json.JSONDecodeError:
            # Try to repair truncated JSON
            repaired = _repair_json(fragment)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass
    raise ValueError(f"AI did not return valid JSON:\n{raw[:500]}")

def _client() -> Groq:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    return Groq(api_key=key)

def extract(doc_texts: dict) -> dict:
    # Groq account TPM limit for this model is 8000 tokens (prompt + max_tokens combined).
    # OCR'd/dense source text can tokenize well above a chars/4 estimate, so cap input
    # conservatively: each doc to 1200 chars, total combined to 4500 chars, and trim
    # the output budget to leave headroom.
    combined = "\n\n".join(f"=== {k} ===\n{v[:1200]}" for k, v in doc_texts.items())
    resp = _client().chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": combined[:4500]},
        ],
        temperature=0.1, max_tokens=2200,
        reasoning_effort="low", reasoning_format="hidden",
    )
    return _parse(resp.choices[0].message.content)

def extract_remote_staff(doc_texts: dict) -> dict:
    combined = "\n\n".join(f"=== {k} ===\n{v[:2500]}" for k, v in doc_texts.items())
    resp = _client().chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": STAFF_PROMPT},
            {"role": "user", "content": combined[:9000]},
        ],
        temperature=0.1, max_tokens=2200,
        reasoning_effort="low", reasoning_format="hidden",
    )
    return _parse(resp.choices[0].message.content)

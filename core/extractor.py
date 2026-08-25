"""extractor.py — Groq AI extraction. Reads GROQ_API_KEY from environment."""
import os, json, re
from groq import Groq

EXTRACTION_PROMPT = """
You are a document analysis assistant. Extract the following from the document text and return ONLY valid JSON — no markdown, no explanation.

{
  "parent_name": "",
  "parent_reg_no": "",
  "parent_ref_no": "",
  "parent_reg_date": "",
  "parent_address": "",
  "parent_directors": [],
  "ao_full_name": "",
  "ao_dob": "",
  "ao_passport": "",
  "ao_nationality": "",
  "ao_position": "",
  "ao_uk_title": "",
  "ao_soc_code": "",
  "ao_going_rate": "",
  "ao_going_rate_hourly": "",
  "application_date": ""
}

Rules:
- parent_name: full business/company name (e.g. M/S AL-HABIB ENGINEERING & CONTRACTOR)
- parent_reg_no: SECP/CTRN registration number
- parent_ref_no: reference number if shown
- parent_reg_date: formatted as DD Month YYYY
- parent_directors: list of director/owner/partner full names
- ao_uk_title: proposed UK job title (default "Executive Director" if unclear)
- ao_soc_code: SOC 2020 code (default "1111" if unclear)
- ao_going_rate: annual salary e.g. "£60,000"
- ao_going_rate_hourly: e.g. "£30.77 per hour"
- Return "" for any field not found
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

def _parse(raw: str) -> dict:
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise ValueError(f"AI did not return valid JSON:\n{raw[:500]}")

def _client() -> Groq:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    return Groq(api_key=key)

def extract(doc_texts: dict) -> dict:
    combined = "\n\n".join(f"=== {k} ===\n{v[:4000]}" for k, v in doc_texts.items())
    resp = _client().chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": combined[:12000]},
        ],
        temperature=0.1, max_tokens=1500,
    )
    return _parse(resp.choices[0].message.content)

def extract_remote_staff(doc_texts: dict) -> dict:
    combined = "\n\n".join(f"=== {k} ===\n{v[:5000]}" for k, v in doc_texts.items())
    resp = _client().chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[
            {"role": "system", "content": STAFF_PROMPT},
            {"role": "user", "content": combined[:14000]},
        ],
        temperature=0.1, max_tokens=2000,
    )
    return _parse(resp.choices[0].message.content)

"""draft_generator.py — generates all documents as bytes, packages as ZIP."""
import io, zipfile, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import templates.a1_title_pages as a1
import templates.b1_consultancy_agreement as b1
from core import renderer
import templates.c1_employment_letter as c1
import templates.c2_board_resolution as c2
import templates.c3_ao_details as c3
import templates.c8_statement_of_truth as c8
import templates.e10_employment_contract as e10
import templates.f28_remote_staff as f28


def generate_phase1_zip(fields: dict, uk_fields: dict, extra: dict = None) -> bytes:
    """Generate all Phase 1 documents and return as a ZIP file (bytes)."""
    extra = extra or {}
    client_name = fields.get("ao_full_name", "client").replace("/", "-")
    parent_safe = fields.get("parent_name", "documents").replace("/", "-").replace("\\", "-")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        def add(annex_folder, filename, gen_fn, **kwargs):
            try:
                data = gen_fn(**kwargs)
                if isinstance(data, bytes):
                    zf.writestr(f"{annex_folder}/{filename}", data)
                    return True
                return False
            except Exception as e:
                zf.writestr(f"{annex_folder}/{filename}.ERROR.txt", str(e))
                return False

        def _a1():
            if renderer.has_template("A1"):
                ctx = renderer.build_context("A1", fields, uk_fields, extra)
                return renderer.render("A1", ctx)
            return a1.generate(fields, uk_fields, output_path=None)

        add("ANNEX A", "ANNEX A.1 - Title Pages.docx", _a1)

        add("ANNEX B", "ANNEX B.1 - Consultancy Agreement.docx",
            lambda: b1.generate(fields, uk_fields, output_path=None,
                                agreement_date=extra.get("agreement_date", "")))

        add("ANNEX C", "ANNEX C.1 - Letter from Company HR, confirming Employment.docx",
            lambda: c1.generate(fields, uk_fields, output_path=None,
                                salary=extra.get("salary", ""),
                                start_date=extra.get("start_date", ""),
                                doc_date=extra.get("c1_doc_date", "")))

        add("ANNEX C",
            "ANNEX C.2 - Board Resolution – Minutes of Meeting from the Parent Company.docx",
            lambda: c2.generate(fields, uk_fields, output_path=None,
                                meeting_date=extra.get("meeting_date", ""),
                                directors=fields.get("parent_directors", []),
                                attendees=extra.get("attendees", [])))

        add("ANNEX C", "ANNEX C.3 - AO Details.docx",
            lambda: c3.generate(fields, uk_fields, output_path=None,
                                doc_date=extra.get("c3_doc_date", "")))

        add("ANNEX C", "ANNEX C.8 - AO – Statement of Truth.docx",
            lambda: c8.generate(fields, uk_fields, output_path=None,
                                doc_date=extra.get("doc_date", "")))

        add("ANNEX E", "ANNEX E.12 - Employment Contract – Draft Copy.docx",
            lambda: e10.generate(fields, uk_fields, output_path=None,
                                 salary=extra.get("salary", ""),
                                 start_date=extra.get("start_date", "")))

    buf.seek(0)
    return buf.read()


def generate_f28_bytes(fields: dict, uk_fields: dict, staff_data: dict) -> bytes:
    """Generate F.2.8 document and return as bytes."""
    return f28.generate(fields, uk_fields, staff_data, output_path=None)

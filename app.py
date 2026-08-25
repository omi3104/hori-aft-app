"""
Expansion Drafter — Streamlit Web App
"""

import os, sys, io
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from core import companies_house, document_reader, extractor, draft_generator

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Expansion Drafter",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Main background ── */
    .stApp { background: #f0f2f7; }
    .main .block-container { padding-top: 1.5rem; }

    /* ── Sidebar — deep charcoal ── */
    section[data-testid="stSidebar"] {
        background: #0d0f14 !important;
        border-right: 1px solid #1e2332;
    }
    section[data-testid="stSidebar"] * { color: #c8cdd8 !important; }
    section[data-testid="stSidebar"] .stButton button {
        background: #1a1d27 !important;
        border: 1px solid #2a2f3e !important;
        color: #c8cdd8 !important;
        border-radius: 10px !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        transition: all 0.18s ease;
        text-align: left !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #252a38 !important;
        border-color: #3d8ef8 !important;
        color: #ffffff !important;
    }

    /* ── Main header ── */
    .main-header {
        background: #0d0f14;
        color: white; padding: 26px 32px;
        border-radius: 16px; margin-bottom: 24px;
        border: 1px solid #1e2332;
        position: relative; overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #3d8ef8, #7c3aed, #ec4899);
    }
    .main-header h1 {
        margin: 0; font-size: 1.8rem; font-weight: 800;
        letter-spacing: -0.5px; color: #ffffff;
    }
    .main-header p {
        margin: 6px 0 0; font-size: 0.92rem;
        color: #6b7280; font-weight: 400;
    }

    /* ── Client cards ── */
    .client-card {
        border: 1px solid #e5e9f2;
        border-left: 4px solid #3d8ef8;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        background: #ffffff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: all 0.18s ease;
    }
    .client-card:hover {
        box-shadow: 0 4px 20px rgba(61,142,248,0.12);
        border-left-color: #7c3aed;
        transform: translateX(2px);
    }

    /* ── Status badges ── */
    .badge {
        display: inline-block; padding: 3px 10px;
        border-radius: 6px; font-size: 0.75rem; font-weight: 700;
        letter-spacing: 0.02em;
    }
    .badge-grey   { background: #f1f3f9; color: #6b7280; }
    .badge-orange { background: #fff4e6; color: #d97706; border: 1px solid #fcd34d; }
    .badge-green  { background: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }

    /* ── Step progress bar ── */
    .step-bar {
        display: flex; gap: 4px; margin-bottom: 28px;
    }
    .step-item {
        flex: 1; padding: 14px 10px; text-align: center;
        font-size: 0.8rem; font-weight: 600;
        background: #ffffff; color: #9ca3af;
        border-radius: 10px;
        border: 1px solid #e5e9f2;
    }
    .step-item.done {
        background: #eff6ff; color: #3d8ef8;
        border-color: #bfdbfe;
    }
    .step-item.active {
        background: #0d0f14; color: #ffffff;
        border-color: #0d0f14;
        box-shadow: 0 4px 14px rgba(13,15,20,0.25);
    }
    .step-item.active .step-num { color: #3d8ef8; }
    .step-num { display: block; font-size: 1rem; margin-bottom: 3px; }

    /* ── Info / note boxes ── */
    .step-box {
        background: #f0f7ff; border-left: 4px solid #3d8ef8;
        padding: 12px 18px; border-radius: 8px; margin: 14px 0;
        font-size: 0.91rem; color: #1e40af;
    }
    .note-box {
        background: #fffbeb; border-left: 4px solid #f59e0b;
        padding: 10px 16px; border-radius: 8px; margin: 10px 0;
        font-size: 0.87rem; color: #92400e;
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 0.7rem; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: #9ca3af;
        margin: 24px 0 12px; padding-bottom: 8px;
        border-bottom: 2px solid #e5e9f2;
    }

    /* ── Download button ── */
    div[data-testid="stDownloadButton"] button {
        background: #0d0f14 !important;
        color: white !important; border-radius: 10px !important;
        border: none !important; font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.18s ease !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background: #3d8ef8 !important;
        box-shadow: 0 4px 16px rgba(61,142,248,0.4) !important;
    }

    /* ── Primary buttons ── */
    .stButton button[kind="primary"], .stButton [data-testid*="primary"] button {
        background: #0d0f14 !important;
        border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; color: white !important;
    }

    /* ── Regular buttons in main area ── */
    .main .stButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #d1d9e6 !important;
        background: #ffffff !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3d8ef8 !important;
        box-shadow: 0 0 0 3px rgba(61,142,248,0.12) !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-weight: 700 !important; font-size: 0.9rem !important;
        background: #f8fafc !important; border-radius: 8px !important;
        border: 1px solid #e5e9f2 !important;
    }

    /* ── Stat cards in sidebar ── */
    .stat-card {
        background: #1a1d27; border: 1px solid #2a2f3e;
        border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .stat-label { font-size: 0.78rem; color: #6b7280 !important; }
    .stat-value { font-size: 1.1rem; font-weight: 800; color: #ffffff !important; }

    /* ── Divider ── */
    hr { border-color: #1e2332 !important; margin: 12px 0 !important; }

    /* ── Success / error messages ── */
    .stSuccess { border-radius: 10px !important; }
    .stError   { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "clients" not in st.session_state:
    st.session_state.clients = []
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "new_client" not in st.session_state:
    st.session_state.new_client = {}

groq_ok = bool(os.environ.get("GROQ_API_KEY"))
ch_ok   = bool(os.environ.get("CH_API_KEY"))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 4px 20px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <span style="font-size:1.4rem;">🏛️</span>
        <span style="font-size:1.1rem; font-weight:800; color:#ffffff; letter-spacing:-0.3px;">Expansion Drafter</span>
      </div>
      <div style="font-size:0.73rem; color:#4b5563; letter-spacing:0.05em; text-transform:uppercase; font-weight:600;">UK Sponsor Licence System</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("📋  Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
    if st.button("➕  New Client", use_container_width=True):
        st.session_state.page = "new_client"
        st.session_state.new_client = {}
        st.rerun()

    st.divider()

    total = len(st.session_state.clients)
    done1 = sum(1 for c in st.session_state.clients if c.get("phase1_done"))
    done2 = sum(1 for c in st.session_state.clients if c.get("phase2_done"))
    st.markdown(f"""
    <div style="font-size:0.68rem; font-weight:800; color:#4b5563; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:10px;">Overview</div>
    <div class="stat-card"><span class="stat-label">Total Clients</span><span class="stat-value">{total}</span></div>
    <div class="stat-card"><span class="stat-label">Phase 1 Done</span><span class="stat-value" style="color:#f59e0b !important;">{done1}</span></div>
    <div class="stat-card"><span class="stat-label">Fully Complete</span><span class="stat-value" style="color:#10b981 !important;">{done2}</span></div>
    """, unsafe_allow_html=True)

    if not groq_ok or not ch_ok:
        st.divider()
        if not groq_ok:
            st.warning("⚠️ AI service not configured")
        if not ch_ok:
            st.warning("⚠️ Company lookup not configured")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🏛️ Expansion Drafter</h1>
  <p>UK Expansion Worker Sponsor Licence &nbsp;·&nbsp; Automated Document Generator</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":
    st.markdown('<div class="section-header">Client Cases</div>', unsafe_allow_html=True)

    if not st.session_state.clients:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; background:#f8fafc;
             border-radius:16px; border:2px dashed #e2e8f0; color:#94a3b8;">
          <div style="font-size:2.5rem; margin-bottom:12px;">📂</div>
          <div style="font-size:1.1rem; font-weight:600; color:#64748b;">No clients yet</div>
          <div style="font-size:0.9rem; margin-top:6px;">Click <b>➕ New Client</b> in the sidebar to begin</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, client in enumerate(st.session_state.clients):
            name    = client.get("name", "Unknown")
            uk_name = client.get("uk_fields", {}).get("company_name", "")
            phase1  = client.get("phase1_done", False)
            phase2  = client.get("phase2_done", False)

            if phase1 and phase2:
                badge = '<span class="badge badge-green">✓ Complete</span>'
            elif phase1:
                badge = '<span class="badge badge-orange">Phase 1 Done</span>'
            else:
                badge = '<span class="badge badge-grey">In Progress</span>'

            with st.container():
                st.markdown(f"""
                <div class="client-card">
                  <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                    <span style="font-size:1.05rem; font-weight:700; color:#0f1f3d;">{name}</span>
                    {badge}
                  </div>
                  <div style="font-size:0.82rem; color:#94a3b8;">{uk_name}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                # Phase 1 ZIP download
                if phase1 and client.get("phase1_zip"):
                    with col1:
                        safe = name.replace(" ", "_").replace("/", "-")[:30]
                        st.download_button(
                            "📥 Download Phase 1 ZIP",
                            data=client["phase1_zip"],
                            file_name=f"{safe}_Phase1_Drafts.zip",
                            mime="application/zip",
                            key=f"dl1_{i}",
                        )

                # Phase 2 F.2.8 download
                if phase2 and client.get("f28_bytes"):
                    with col2:
                        safe = name.replace(" ", "_").replace("/", "-")[:30]
                        st.download_button(
                            "📥 Download F.2.8",
                            data=client["f28_bytes"],
                            file_name=f"{safe}_F2.8_Remote_Staff.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl2_{i}",
                        )

                # Phase 2 upload (if phase 1 done but not phase 2)
                if phase1 and not phase2:
                    with col2:
                        if st.button("📂 Add F.2.8 Remote Staff", key=f"p2_{i}"):
                            st.session_state.page = "phase2"
                            st.session_state.phase2_client_idx = i
                            st.rerun()

                with col4:
                    if st.button("🗑 Remove", key=f"rm_{i}"):
                        st.session_state.clients.pop(i)
                        st.rerun()

                st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: NEW CLIENT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "new_client":

    nc = st.session_state.new_client
    step = nc.get("step", 1)

    st.subheader("New Client — Step by Step")

    # Progress indicator
    steps = ["1. Company Details", "2. Upload Documents", "3. Review & Edit", "4. Generate & Download"]
    cols = st.columns(4)
    for j, s in enumerate(steps):
        with cols[j]:
            if j + 1 < step:
                st.success(s)
            elif j + 1 == step:
                st.info(f"**{s}**")
            else:
                st.markdown(f"<span style='color:#aaa'>{s}</span>", unsafe_allow_html=True)

    st.divider()

    # ── STEP 1: Company details ───────────────────────────────────────────────
    if step == 1:
        st.markdown('<div class="step-box"><b>Step 1:</b> Enter client name and look up the UK company.</div>',
                    unsafe_allow_html=True)

        client_name = st.text_input("Client / Case Name",
                                     value=nc.get("name", ""),
                                     placeholder="e.g. M/S AL-MAKKAH EXPORTS")
        uk_num = st.text_input("UK Company Number",
                                value=nc.get("uk_num", ""),
                                placeholder="e.g. 17395793  (8 digits)")

        col1, col2 = st.columns([1, 3])
        with col1:
            lookup = st.button("🔍 Lookup Company", type="primary")

        if lookup:
            if not uk_num.strip():
                st.error("Enter a UK company number first.")
            elif not ch_ok:
                st.error("Companies House API key not configured. Contact your administrator.")
            else:
                with st.spinner("Fetching from Companies House..."):
                    try:
                        uk_fields = companies_house.get_company(uk_num.strip())
                        nc["uk_fields"] = uk_fields
                        nc["name"]      = client_name or uk_fields["company_name"]
                        nc["uk_num"]    = uk_num
                        st.success(f"✅ Found: **{uk_fields['company_name']}** | "
                                   f"Inc: {uk_fields['incorporation_date']} | "
                                   f"{uk_fields['registered_address'][:60]}...")
                        if uk_fields.get("sic_codes"):
                            st.caption(f"SIC codes: {', '.join(uk_fields['sic_codes'])}")
                    except Exception as e:
                        st.error(f"Lookup failed: {e}")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Next →", type="primary",
                         disabled=not nc.get("uk_fields") or not client_name.strip()):
                nc["name"] = client_name.strip()
                nc["step"] = 2
                st.rerun()
        with col_b:
            if nc.get("uk_fields"):
                st.markdown('<div class="note-box">✅ Company found. Click <b>Next</b> to upload documents.</div>',
                            unsafe_allow_html=True)

    # ── STEP 2: Upload documents ──────────────────────────────────────────────
    elif step == 2:
        st.markdown('<div class="step-box"><b>Step 2:</b> Upload the client documents for AI extraction.</div>',
                    unsafe_allow_html=True)

        st.markdown("#### Required Documents")
        st.markdown("""
        - 📄 **Parent company registration certificate** (SECP/CTRN)
        - 🪪 **AO / employee passport** (scan)
        - 📋 **AO / employee CV or résumé**
        """)

        uploaded = st.file_uploader(
            "Select required files (hold Ctrl to select multiple)",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="doc_upload",
        )

        st.divider()
        st.markdown("#### Optional — Recommended for Better Drafts")
        st.markdown("""
        - 🏢 **Business Profile** — used to extract job description and duties for C.1 Employment Letter
        - 📊 **Hierarchy / Organisational Chart** — used to confirm reporting structure and job title
        """)

        uploaded_optional = st.file_uploader(
            "Select optional files (Business Profile, Org Chart)",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="optional_upload",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back"):
                nc["step"] = 1
                st.rerun()
        with col2:
            if st.button("🤖 Extract Data →", type="primary",
                         disabled=not uploaded or not groq_ok):
                doc_texts = {}
                with st.spinner("Reading documents..."):
                    for uf in (uploaded or []):
                        try:
                            doc_texts[uf.name] = document_reader.read_uploaded(
                                uf.read(), uf.name)
                        except Exception as e:
                            st.warning(f"Could not read {uf.name}: {e}")
                    for uf in (uploaded_optional or []):
                        try:
                            doc_texts[f"[OPTIONAL] {uf.name}"] = document_reader.read_uploaded(
                                uf.read(), uf.name)
                        except Exception as e:
                            st.warning(f"Could not read {uf.name}: {e}")

                if not doc_texts:
                    st.error("No text could be extracted from the uploaded files.")
                else:
                    with st.spinner("Sending to AI (Groq)... usually 5–15 seconds"):
                        try:
                            fields = extractor.extract(doc_texts)
                            nc["fields"] = fields
                            nc["step"]   = 3
                            st.rerun()
                        except Exception as e:
                            st.error(f"AI extraction failed: {e}")

        if not groq_ok:
            st.warning("⚠️ Groq API key not configured. Cannot extract data.")

    # ── STEP 3: Review & edit ─────────────────────────────────────────────────
    elif step == 3:
        st.markdown('<div class="step-box"><b>Step 3:</b> Review every field. Edit anything wrong or missing. Then generate.</div>',
                    unsafe_allow_html=True)

        fields    = nc.get("fields", {})
        uk_fields = nc.get("uk_fields", {})

        # ── UK Subsidiary (read-only) ──────────────────────────────────────────
        st.markdown("#### 🏢 UK Subsidiary *(from Companies House — read-only)*")
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("UK Company Name", uk_fields.get("company_name",""), disabled=True)
        with c2: st.text_input("Company Number",  uk_fields.get("company_number",""), disabled=True)
        with c3: st.text_input("Incorporated On", uk_fields.get("incorporation_date",""), disabled=True)
        st.text_input("UK Registered Address", uk_fields.get("registered_address",""), disabled=True)

        # ── Parent Company ─────────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 🏭 Parent Company *(AI-extracted — edit if wrong)*")

        c1, c2 = st.columns(2)
        with c1:
            fields["parent_name"]     = st.text_input("Parent Company Name", fields.get("parent_name",""))
            fields["parent_reg_no"]   = st.text_input("Registration Number", fields.get("parent_reg_no",""))
            fields["parent_ref_no"]   = st.text_input("Reference No.", fields.get("parent_ref_no",""))
        with c2:
            fields["parent_reg_date"] = st.text_input("Registered On (DD Month YYYY)", fields.get("parent_reg_date",""))
            fields["parent_address"]  = st.text_input("Registered Address", fields.get("parent_address",""))
            fields["parent_website"]   = st.text_input("Company Website", fields.get("parent_website",""),
                                                        help="Used in A.1 Title Pages table")

        c1, c2 = st.columns(2)
        with c1:
            fields["parent_activity"] = st.text_input("Business Principal Activity / SIC Code",
                                                       fields.get("parent_activity",""),
                                                       placeholder="e.g. 890173 – Other Service Activities",
                                                       help="Shown in A.1 Parent Company table")
        with c2:
            fields["company_type"]    = st.selectbox("Entity Type (for E.12)",
                                                      ["", "Sole Proprietorship", "Association of Persons",
                                                       "Private Limited", "Partnership", "Public Limited"],
                                                      index=["", "Sole Proprietorship", "Association of Persons",
                                                             "Private Limited", "Partnership", "Public Limited"]
                                                             .index(fields.get("company_type",""))
                                                             if fields.get("company_type","") in
                                                             ["", "Sole Proprietorship", "Association of Persons",
                                                              "Private Limited", "Partnership", "Public Limited"]
                                                             else 0)

        dirs_raw = st.text_area("Directors / Partners (one per line)",
                                 "\n".join(fields.get("parent_directors", [])), height=80)
        fields["parent_directors"] = [d.strip() for d in dirs_raw.split("\n") if d.strip()]

        # ── Authorising Officer ────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 👤 Authorising Officer *(AI-extracted — edit if wrong)*")

        c1, c2, c3 = st.columns(3)
        with c1:
            fields["ao_full_name"]  = st.text_input("AO Full Name", fields.get("ao_full_name",""))
            fields["ao_dob"]        = st.text_input("Date of Birth", fields.get("ao_dob",""))
        with c2:
            fields["ao_passport"]   = st.text_input("Passport Number", fields.get("ao_passport",""))
            fields["ao_nationality"]= st.text_input("Nationality", fields.get("ao_nationality",""))
        with c3:
            fields["ao_position"]   = st.text_input("Position in Parent Company", fields.get("ao_position",""))

        # ── Job Description ────────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 💼 Job Description *(from Business Profile / CV)*")

        c1, c2 = st.columns(2)
        with c1:
            fields["reporting_to"] = st.text_input("Reports To", fields.get("reporting_to",""))
        with c2:
            fields["department"]   = st.text_input("Department / Division", fields.get("department",""))

        fields["job_description"] = st.text_area(
            "Job Description (paragraph)",
            fields.get("job_description",""),
            height=100,
            help="Extracted from Business Profile. Edit if needed.",
        )
        duties_raw = st.text_area(
            "Key Duties / Responsibilities (one per line)",
            "\n".join(fields.get("job_duties", [])),
            height=120,
            help="Extracted from Business Profile or CV. Edit if needed.",
        )
        fields["job_duties"] = [d.strip() for d in duties_raw.split("\n") if d.strip()]

        # ══════════════════════════════════════════════════════════════════════
        # PER-DOCUMENT DETAILS
        # ══════════════════════════════════════════════════════════════════════
        st.divider()
        st.markdown("#### 📋 Per-Document Details")
        st.markdown('<div class="note-box">Complete the fields below for each draft. Dates can be entered as DD Month YYYY or DD/MM/YYYY.</div>',
                    unsafe_allow_html=True)

        # ── A.1 Title Pages ───────────────────────────────────────────────────
        with st.expander("📄 A.1 — Title Pages", expanded=True):
            st.caption("Note: Company Website is in the Parent Company section above.")

        # ── B.1 Consultancy Agreement ─────────────────────────────────────────
        with st.expander("📋 B.1 — Consultancy Agreement", expanded=True):
            extra_agr_date = st.text_input("Date of Agreement", "",
                                            key="agr_date",
                                            placeholder="e.g. 22 April 2026",
                                            help="The date this consultancy agreement was signed")

        # ── C.1 Employment Confirmation Letter ────────────────────────────────
        with st.expander("📝 C.1 — Employment Confirmation Letter (HR Letter)", expanded=True):
            c1a, c1b, c1c = st.columns(3)
            with c1a:
                extra_c1_date  = st.text_input("Date of Letter", "", key="c1_date",
                                                placeholder="e.g. 08 May 2026")
            with c1b:
                extra_start    = st.text_input("Employment Start Date", "", key="start_date",
                                                placeholder="e.g. 01 January 2020")
            with c1c:
                extra_salary   = st.text_input("Salary (if different from going rate)", "",
                                                key="salary")

        # ── C.2 Board Resolution ──────────────────────────────────────────────
        with st.expander("📋 C.2 — Board Resolution / Minutes of Meeting", expanded=True):
            c2a, c2b = st.columns(2)
            with c2a:
                extra_mtg_date = st.text_input("Date of Meeting", "", key="mtg_date",
                                                placeholder="e.g. 09 February 2026")
            with c2b:
                st.caption("Attendees extracted from Hierarchy Chart — confirm below.")

            # Pre-populate attendees from AI-extracted board_attendees or directors
            extracted_attendees = fields.get("board_attendees", [])
            if not extracted_attendees:
                # Fall back: build from directors with their designations (name only if no designation info)
                extracted_attendees = fields.get("parent_directors", [])

            attendees_raw = st.text_area(
                "Board Meeting Attendees — one per line, format: Name, Designation",
                "\n".join(extracted_attendees),
                height=120,
                key="attendees",
                help="E.g.: Muhammad Usman, Chief Executive Officer\nSara Ahmed, Finance Manager\n"
                     "These names & titles appear in Section 1 (Attendance) of the Board Resolution.",
            )
            attendees_list = [a.strip() for a in attendees_raw.split("\n") if a.strip()]

            if not attendees_list:
                st.warning("⚠️ No attendees entered. Upload a Hierarchy Chart in Step 2 for automatic extraction, or type them above.")

        # ── C.3 AO Details ────────────────────────────────────────────────────
        with st.expander("📄 C.3 — AO Details (Letter to Home Office)", expanded=True):
            st.caption("UK job role details for C.3 — confirm or edit below.")
            c3a, c3b, c3c, c3d = st.columns(4)
            with c3a:
                fields["ao_uk_title"]  = st.text_input("UK Proposed Job Title",
                                                         fields.get("ao_uk_title","Executive Director"),
                                                         key="c3_title")
            with c3b:
                fields["ao_soc_code"]  = st.text_input("SOC Code",
                                                         fields.get("ao_soc_code","1111"),
                                                         key="c3_soc")
            with c3c:
                fields["ao_going_rate"] = st.text_input("Annual Salary / Going Rate",
                                                          fields.get("ao_going_rate","£60,000"),
                                                          key="c3_rate")
            with c3d:
                fields["ao_going_rate_hourly"] = st.text_input("Hourly Rate",
                                                                 fields.get("ao_going_rate_hourly","£30.77 per hour"),
                                                                 key="c3_hourly")
            extra_c3_date = st.text_input("Date of Letter", "", key="c3_date",
                                           placeholder="e.g. 08 May 2026")

        # ── C.8 Statement of Truth ────────────────────────────────────────────
        with st.expander("✍️ C.8 — Statement of Truth (by Authorising Officer)", expanded=True):
            extra_doc_date = st.text_input("Date Signed", "", key="c8_date",
                                            placeholder="e.g. 08-05-2026")

        # ── E.12 Employment Contract ───────────────────────────────────────────
        with st.expander("📋 E.12 — Employment Contract", expanded=True):
            st.caption("Start date and salary come from C.1 fields above.")

        # ══════════════════════════════════════════════════════════════════════
        nc["fields"] = fields
        nc["extra"]  = {
            "salary":         extra_salary,
            "start_date":     extra_start,
            "agreement_date": extra_agr_date,
            "meeting_date":   extra_mtg_date,
            "doc_date":       extra_doc_date,
            "attendees":      attendees_list,
            "c1_doc_date":    extra_c1_date,
            "c3_doc_date":    extra_c3_date,
        }

        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back"):
                nc["step"] = 2
                st.rerun()
        with col2:
            if st.button("⚡ Generate All Phase 1 Drafts →", type="primary"):
                nc["step"] = 4
                st.rerun()

    # ── STEP 4: Generate & Download ───────────────────────────────────────────
    elif step == 4:
        st.markdown('<div class="step-box"><b>Step 4:</b> Generating all documents — please wait.</div>',
                    unsafe_allow_html=True)

        fields    = nc.get("fields", {})
        uk_fields = nc.get("uk_fields", {})
        extra     = nc.get("extra", {})
        name      = nc.get("name", "client")

        if not nc.get("generated"):
            with st.spinner("Generating A.1, B.1, C.1, C.2, C.3, C.8, E.10..."):
                try:
                    zip_bytes = draft_generator.generate_phase1_zip(fields, uk_fields, extra)
                    nc["generated"]  = True
                    nc["phase1_zip"] = zip_bytes
                except Exception as e:
                    st.error(f"Generation failed: {e}")
                    if st.button("← Go back"):
                        nc["step"] = 3
                        st.rerun()
                    st.stop()

        st.success("✅ All Phase 1 drafts generated successfully!")
        st.markdown("""
        **Your ZIP contains:**
        - ANNEX A / ANNEX A.1 - Title Pages.docx
        - ANNEX B / ANNEX B.1 - Consultancy Agreement.docx
        - ANNEX C / ANNEX C.1 - Employment Confirmation Letter.docx
        - ANNEX C / ANNEX C.2 - Board Resolution.docx
        - ANNEX C / ANNEX C.3 - AO Details.docx
        - ANNEX C / ANNEX C.8 - Statement of Truth.docx
        - ANNEX E / ANNEX E.10 - Employment Contract.docx
        """)

        safe = name.replace(" ", "_").replace("/", "-")[:40]
        st.download_button(
            "📥 Download Phase 1 ZIP",
            data=nc["phase1_zip"],
            file_name=f"{safe}_Phase1_Drafts.zip",
            mime="application/zip",
            type="primary",
        )

        st.divider()
        st.markdown("#### What's next?")
        st.markdown("When your **org chart / staff list** is ready, come back to add **F.2.8 Remote Staff** from the dashboard.")

        if st.button("✅ Save Client & Go to Dashboard", type="primary"):
            st.session_state.clients.append({
                "name":       name,
                "uk_fields":  uk_fields,
                "fields":     fields,
                "phase1_done": True,
                "phase2_done": False,
                "phase1_zip": nc["phase1_zip"],
                "f28_bytes":  None,
            })
            st.session_state.page = "dashboard"
            st.session_state.new_client = {}
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PHASE 2 — REMOTE STAFF
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "phase2":
    idx    = st.session_state.get("phase2_client_idx", 0)
    client = st.session_state.clients[idx]
    name   = client.get("name", "")

    st.subheader(f"Phase 2 — F.2.8 Remote Staff: {name}")
    st.markdown('<div class="step-box">Upload the org chart or staff list. AI will extract staff names, roles, and salaries.</div>',
                unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Org chart / Staff list (PDF, DOCX, or Excel)",
        type=["pdf", "docx", "doc", "xlsx", "csv"],
        accept_multiple_files=True,
        key="staff_upload",
    )

    if uploaded:
        if st.button("🤖 Extract Staff Data", type="primary"):
            doc_texts = {}
            with st.spinner("Reading staff documents..."):
                for uf in uploaded:
                    try:
                        doc_texts[uf.name] = document_reader.read_uploaded(uf.read(), uf.name)
                    except Exception as e:
                        st.warning(f"Could not read {uf.name}: {e}")

            with st.spinner("Extracting staff data with AI..."):
                try:
                    staff_data = extractor.extract_remote_staff(doc_texts)
                    st.session_state.staff_data = staff_data
                    st.rerun()
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

    if "staff_data" in st.session_state:
        staff_data = st.session_state.staff_data
        staff_list = staff_data.get("staff", [])

        if not staff_list:
            st.warning("No staff found in the documents. Try uploading a clearer document.")
        else:
            st.success(f"✅ Found {len(staff_list)} staff member(s):")
            for s in staff_list:
                st.markdown(f"- **{s.get('name','')}** — {s.get('parent_role','')} → {s.get('uk_role','')} ({s.get('weekly_hours',8)} hrs/week)")

            st.divider()
            if st.button("⚡ Generate F.2.8", type="primary"):
                with st.spinner("Generating F.2.8..."):
                    try:
                        f28_bytes = draft_generator.generate_f28_bytes(
                            client["fields"], client["uk_fields"], staff_data)
                        st.session_state.clients[idx]["phase2_done"] = True
                        st.session_state.clients[idx]["f28_bytes"]   = f28_bytes
                        del st.session_state.staff_data
                        st.session_state.page = "dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    if st.button("← Back to Dashboard"):
        if "staff_data" in st.session_state:
            del st.session_state.staff_data
        st.session_state.page = "dashboard"
        st.rerun()

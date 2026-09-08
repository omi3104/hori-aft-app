# Hori-aft

UK **Expansion Worker** (Global Business Mobility) sponsor-licence document generator.
Upload a client's incorporation / corporate papers, let the AI extract the fields,
review them, and download the drafted application documents (A.1, B.1, C.1, C.2,
C.3, C.8, E.10, F.2.8) as `.docx`.

Built with Streamlit. Runs entirely on Streamlit Community Cloud — nothing is
installed on your machine; the desktop icon is just a shortcut to the app URL.

## How it works

| Stage | Engine |
|-------|--------|
| Read uploads (PDF / DOCX / image) | PyMuPDF + Tesseract OCR fallback |
| Extract structured fields | Groq API — `openai/gpt-oss-20b` |
| UK company lookup | Companies House REST API |
| SIC code descriptions | bundled `core/sic_lookup.py` table |
| Draft generation | `python-docx` templates in `templates/` |

## Secrets

The app needs two keys. On Streamlit Community Cloud set them in
**App → Settings → Secrets**; for a local run copy
`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.

```toml
GROQ_API_KEY = "gsk_..."
CH_API_KEY   = "..."
```

- **GROQ_API_KEY** — https://console.groq.com/keys (free tier)
- **CH_API_KEY** — https://developer.company-information.service.gov.uk/ (free; create an application, use the REST API key)

Streamlit Community Cloud also exposes these secrets to the app as environment
variables, which is how `core/extractor.py` and `core/companies_house.py` read them.

## Deploy (one time)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io → **Create app** → pick this repo,
   branch `main`, main file `app.py`.
3. Open **Advanced settings → Secrets**, paste the two keys, deploy.
4. Streamlit installs `requirements.txt` (Python deps) and `packages.txt`
   (`tesseract-ocr`) automatically. Every push to `main` redeploys.

## Desktop icon

After deploy you get a URL like `https://hori-aft.streamlit.app`.

- **Windows:** right-click desktop → New → Shortcut → paste the URL → name it
  `Hori-aft`. Right-click → Properties → Change Icon for a custom icon.
- Or use the provided `Hori-aft.url` (edit the `URL=` line to your real address).

## Local run (optional, for development)

```bash
pip install -r requirements.txt
# needs the tesseract binary on PATH for image OCR
streamlit run app.py
```

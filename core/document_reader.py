"""document_reader.py — extracts text from PDF/DOCX/image file bytes."""
import io, os

def read_uploaded(file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return _pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _docx(file_bytes)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return _image(file_bytes)
    elif ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _pdf(data: bytes) -> str:
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text)
        else:
            try:
                from PIL import Image
                import pytesseract
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                pages.append(pytesseract.image_to_string(img))
            except Exception:
                pass
    doc.close()
    return "\n".join(pages)

def _docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            lines.append(" | ".join(c.text for c in row.cells))
    return "\n".join(lines)

def _image(data: bytes) -> str:
    from PIL import Image
    try:
        import pytesseract
        img = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(img)
    except Exception:
        raise ValueError(
            "Image OCR isn't available on this deployment (Tesseract not installed). "
            "Upload a text-based PDF or a Word document instead."
        )

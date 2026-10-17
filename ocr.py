"""
ocr.py  —  Windows WinRT OCR wrapper (near-instant, no heavy models)

Falls back to pytesseract if WinRT is unavailable (non-Windows / missing package).
"""

from PIL import Image


# ── Try WinRT (fastest on Windows 10/11) ──────────────────────────
try:
    import screen_ocr
    _winrt_reader = screen_ocr.Reader.create_quality_reader()   # quality > speed reader
    _USE_WINRT = True
    print("[OCR] Using Windows WinRT (fast native OCR)")
except Exception:
    _USE_WINRT = False
    print("[OCR] WinRT unavailable — falling back to pytesseract")


def fast_ocr(pil_image: Image.Image) -> str:
    """
    Run OCR on a PIL image and return extracted text.
    ~0.2–0.4 s on most screens with WinRT.
    """
    if _USE_WINRT:
        return _winrt_ocr(pil_image)
    else:
        return _tesseract_ocr(pil_image)


# ── WinRT path ────────────────────────────────────────────────────
def _winrt_ocr(pil_image: Image.Image) -> str:
    # Pass the PIL image directly; extract text with as_string()
    result = _winrt_reader.read_image(pil_image)
    return result.as_string().strip()


# ── Tesseract fallback ────────────────────────────────────────────
def _tesseract_ocr(pil_image: Image.Image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(pil_image).strip()
    except ImportError:
        return ""

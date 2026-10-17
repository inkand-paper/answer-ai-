"""
groq_client.py  —  Sends the screenshot image directly to Groq vision model.
No OCR step needed — the model reads math, symbols, and text from the image itself.
Falls back to text (OCR) if vision fails.
"""

import io
import base64
from groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

VISION_MODEL  = "openai/gpt-oss-20b"   # vision-capable model
FALLBACK_MODEL = GROQ_MODEL             # text-only fallback

VISION_PROMPT = """\
You are a lightning-fast exam assistant looking at a screenshot of a quiz page.

Your job:
1. Find the actual quiz question on screen (ignore browser tabs, bookmarks, nav menus).
2. If multiple-choice options (A/B/C/D) exist, identify the correct one.
3. For math/formula questions, compute the answer step by step if needed.

Respond in EXACTLY this format — never leave blank:
QUESTION: <the question>
ANSWER: <correct answer — include option letter only if you are certain which letter matches>

Rules:
- Be concise. 1-2 lines.
- Trust the visual — math expressions in the image are exactly as shown.
- Always give your best answer even if unsure.
- NEVER return an empty response.
"""

TEXT_PROMPT = """\
You are a lightning-fast exam assistant. You receive raw OCR text from a quiz screen
(may include browser tabs, bookmarks, and irrelevant UI text).

Your job:
1. Identify the actual quiz question (ignore browser UI noise).
2. If multiple-choice options (A/B/C/D or 1/2/3/4), pick the correct one.
3. For math/arithmetic, calculate directly.

Respond in EXACTLY this format — never leave blank:
QUESTION: <the question>
ANSWER: <correct answer text — include letter only if 100% certain of mapping; if grid layout, just give the text>

Rules:
- Be concise. 1-2 lines.
- Option letters from OCR can be wrong in 2-column layouts — trust the text over the letter.
- Always give best guess, never return empty.
- NEVER return an empty response.
"""


# ── Startup model check ──────────────────────────────────────────
def _check_model():
    try:
        models = [m.id for m in client.models.list().data]
        ok = VISION_MODEL in models
        if ok:
            print(f"[Groq] Vision model '{VISION_MODEL}' ready ✓")
        else:
            print(f"[Groq] Vision model '{VISION_MODEL}' NOT found — will use OCR+text fallback")
        return ok
    except Exception as e:
        print(f"[Groq] Could not verify models: {e}")
        return False

_vision_available = _check_model()


# ── Vision path: send image directly ─────────────────────────────
def ask_groq_vision(pil_image) -> str:
    """Send the screenshot image to the vision model — no OCR needed."""
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG", quality=80)
    b64 = base64.b64encode(buf.getvalue()).decode()

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT,
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


# ── Text fallback: OCR text → model ──────────────────────────────
def ask_groq_text(screen_text: str) -> str:
    """Send OCR text to the text model (fallback)."""
    response = client.chat.completions.create(
        model=FALLBACK_MODEL,
        messages=[
            {"role": "system", "content": TEXT_PROMPT},
            {"role": "user",   "content": screen_text},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


# ── Public entry point ────────────────────────────────────────────
def ask_groq(screen_text: str, pil_image=None) -> str:
    """
    Try vision first (reads math perfectly), fall back to OCR text if vision fails.
    """
    if _vision_available and pil_image is not None:
        try:
            answer = ask_groq_vision(pil_image)
            if answer.strip():
                return answer
            print("[Groq] Vision returned empty, falling back to text...")
        except Exception as e:
            print(f"[Groq] Vision failed ({e}), falling back to text...")

    # Fallback: OCR text
    return ask_groq_text(screen_text)

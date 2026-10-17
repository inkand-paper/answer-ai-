# Screen Q&A Tool — Fast Edition

Captures your full screen, reads text with **Windows native WinRT OCR** (~0.2 s),
sends it to **Groq** and shows the answer in a floating popup — typically **under 1 second** total.

---

## Folder structure
```
screen-qa/
├── main.py          ← run this
├── config.py        ← change API key, model, hotkeys, popup corner here
├── ocr.py           ← WinRT OCR wrapper (falls back to tesseract)
├── groq_client.py   ← Groq API call + smart prompt
├── popup.py         ← dark floating popup
└── requirements.txt
```

## Install dependencies (one command)
```powershell
pip install mss pillow groq keyboard "screen-ocr[winrt]"
```

## Run
```powershell
# Run as Administrator (keyboard needs admin for global hotkeys)
python main.py
```

## Hotkeys
| Key | Action |
|---|---|
| `Ctrl + Space` | Capture screen → OCR → Groq → popup |
| `Esc` | Exit |

## Customise
Open `config.py` to change:
- `GROQ_MODEL` — swap to a different Groq model
- `POPUP_CORNER` — `top-right` / `top-left` / `bottom-right` / `bottom-left`
- `POPUP_SECONDS` — how long the popup stays before auto-closing
- `HOTKEY` / `EXIT_KEY`

## Performance
| Step | Typical time |
|---|---|
| Screen capture | ~0.05 s |
| WinRT OCR | ~0.15–0.35 s |
| Groq API | ~0.3–0.5 s |
| **Total** | **~0.5–0.9 s** |

Compared to EasyOCR which could take 5–30 s on CPU.

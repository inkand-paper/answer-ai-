"""
Screen Q&A Tool — Fast Edition
Uses Windows native WinRT OCR (< 0.3s) + Groq API for near-instant answers.
Press Ctrl+Space to capture, popup appears top-right corner.
Press Esc to exit.
"""

import sys
import time
import threading
import tkinter as tk
import keyboard
import mss
from PIL import Image

from ocr import fast_ocr
from groq_client import ask_groq
from popup import show_popup, _kill_active
from config import COOLDOWN, HOTKEY, EXIT_KEY, CROP_TOP, CROP_BOTTOM, CROP_LEFT, CROP_RIGHT


# ──────────────────────────────────────────────
# WORKER
# ──────────────────────────────────────────────
def handle_capture():
    t0 = time.perf_counter()

    # ── 0. Kill any existing popup so it's not captured by OCR ──
    _kill_active()
    time.sleep(0.06)   # 60ms for the window to actually close

    # ── 1. Grab full primary screen ──
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    # Crop out browser chrome (top) and taskbar (bottom) to reduce OCR noise
    w, h = img.size
    left   = CROP_LEFT
    top    = CROP_TOP
    right  = w - CROP_RIGHT
    bottom = h - CROP_BOTTOM
    img = img.crop((left, top, right, bottom))
    print(f"[Capture] cropped to {img.size[0]}x{img.size[1]} (skipped top={CROP_TOP}px, bottom={CROP_BOTTOM}px)")

    t1 = time.perf_counter()

    # ── 2. OCR (WinRT — very fast) ──
    text = fast_ocr(img)
    t2 = time.perf_counter()

    print(f"[OCR {t2-t1:.2f}s | {len(text)} chars]")
    if text:
        # Print first 300 chars of OCR so we can see what was captured
        preview = text[:300].replace('\n', ' ')
        print(f"[OCR preview]: {preview}")
    else:
        show_popup("⚠ No text found on screen.\nMake the question visible and try again.")
        return

    # ── 3. Ask Groq (vision first, OCR text as fallback) ──
    try:
        answer = ask_groq(text, pil_image=img)
    except Exception as e:
        show_popup(f"Groq error:\n{e}")
        return

    t3 = time.perf_counter()
    print(f"[Groq {t3-t2:.2f}s | total {t3-t0:.2f}s]")
    print(f"[Raw answer]: '{answer}'")
    print('─' * 50)

    # Fallback if model returned nothing — retry once
    if not answer.strip():
        print("[!] Empty response, retrying Groq...")
        try:
            answer = ask_groq(text)
        except Exception:
            pass

    if not answer.strip():
        answer = "⚠ Groq returned an empty response.\nTry pressing Ctrl+Space again."

    show_popup(answer)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("╔══════════════════════════════════════════╗")
    print("║   Screen Q&A Tool  —  Fast WinRT Edition ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  {HOTKEY.upper():<10}  →  capture & answer          ║")
    print(f"║  {EXIT_KEY.upper():<10}  →  exit                          ║")
    print("╚══════════════════════════════════════════╝\n")

    last = 0.0

    while True:
        if keyboard.is_pressed(HOTKEY):
            now = time.time()
            if now - last < COOLDOWN:
                time.sleep(0.05)
                continue
            last = now
            print("\n[Triggered — capturing screen...]")
            t = threading.Thread(target=handle_capture, daemon=True)
            t.start()
            # Do NOT join — popup runs in its own thread, hotkey stays live
            time.sleep(0.3)

        if keyboard.is_pressed(EXIT_KEY):
            print("Bye!")
            break

        time.sleep(0.05)


if __name__ == "__main__":
    main()

"""
popup.py  —  Thread-safe corner popup using a single dedicated tkinter thread.

ALL tkinter calls happen on _tk_worker's thread.
Other threads communicate via _queue — zero race conditions.
"""

import tkinter as tk
import threading
import queue
import ctypes
from config import (
    POPUP_WIDTH, POPUP_HEIGHT, POPUP_MARGIN, POPUP_SECONDS, POPUP_CORNER
)

# ── Colours ───────────────────────────────────────────────────────
BG      = "#111827"
ACCENT  = "#6366f1"
FG_MAIN = "#f1f5f9"
FG_DIM  = "#64748b"
FONT_H  = ("Segoe UI Semibold", 10)
FONT_B  = ("Segoe UI", 11)
FONT_SM = ("Segoe UI", 8)

# ── Internal state (only touched by _tk_worker thread) ───────────
_queue     = queue.Queue()
_root      = None   # hidden master Tk — never destroyed
_popup_win = None   # current Toplevel popup
_after_id  = None   # auto-close after() id


# ─────────────────────────────────────────────────────────────────
# Dedicated tkinter thread
# ─────────────────────────────────────────────────────────────────
def _tk_worker():
    global _root
    _root = tk.Tk()
    _root.withdraw()                  # invisible master window
    _root.after(50, _poll_queue)      # start polling
    _root.mainloop()


def _poll_queue():
    """Called repeatedly on the tkinter thread to process commands."""
    try:
        while True:
            cmd, payload = _queue.get_nowait()
            if cmd == "show":
                _close_popup()
                _create_popup(payload)
            elif cmd == "close":
                _close_popup()
    except queue.Empty:
        pass
    _root.after(30, _poll_queue)


# ─────────────────────────────────────────────────────────────────
# Popup create / close  (always called on the tkinter thread)
# ─────────────────────────────────────────────────────────────────
def _close_popup():
    global _popup_win, _after_id
    if _after_id is not None:
        try:
            _root.after_cancel(_after_id)
        except Exception:
            pass
        _after_id = None
    if _popup_win is not None:
        try:
            _popup_win.destroy()
        except Exception:
            pass
        _popup_win = None


def _create_popup(text: str):
    global _popup_win, _after_id

    win = tk.Toplevel(_root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(bg=BG)

    # ── Position ──────────────────────────────────────────────────
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    W, H, M = POPUP_WIDTH, POPUP_HEIGHT, POPUP_MARGIN
    positions = {
        "top-right":    (sw - W - M, M),
        "top-left":     (M, M),
        "bottom-right": (sw - W - M, sh - H - M),
        "bottom-left":  (M, sh - H - M),
    }
    x, y = positions.get(POPUP_CORNER, positions["top-right"])
    win.geometry(f"{W}x{H}+{x}+{y}")

    # ── Widgets ───────────────────────────────────────────────────
    tk.Frame(win, bg=ACCENT, height=4).pack(fill="x", side="top")
    body = tk.Frame(win, bg=BG, padx=14, pady=10)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="🤖  Answer", bg=BG, fg=ACCENT,
             font=FONT_H, anchor="w").pack(fill="x")
    tk.Frame(body, bg="#1e293b", height=1).pack(fill="x", pady=(4, 6))
    tk.Label(body, text=text, bg=BG, fg=FG_MAIN,
             justify="left", anchor="nw",
             wraplength=W - 36, font=FONT_B).pack(fill="both", expand=True)
    tk.Label(body, text="Click · Esc · auto-closes",
             bg=BG, fg=FG_DIM, font=FONT_SM, anchor="sw").pack(fill="x", side="bottom")

    # ── Close handlers ────────────────────────────────────────────
    def close(_=None):
        _close_popup()

    win.bind("<Button-1>", close)
    win.bind("<Escape>",   close)
    _after_id = _root.after(int(POPUP_SECONDS * 1000), close)

    # ── Hide from screen capture (stays visible on-screen) ────────
    def _hide_from_capture():
        try:
            hwnd = win.winfo_id()
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
        except Exception:
            pass
    _root.after(80, _hide_from_capture)

    _popup_win = win


# ─────────────────────────────────────────────────────────────────
# Public API  (safe to call from any thread)
# ─────────────────────────────────────────────────────────────────
def show_popup(text: str):
    """Show (or replace) the answer popup. Non-blocking."""
    _queue.put(("show", text))


def _kill_active():
    """Close current popup if any. Non-blocking."""
    _queue.put(("close", None))


# ─────────────────────────────────────────────────────────────────
# Start the dedicated tkinter thread on import
# ─────────────────────────────────────────────────────────────────
_thread = threading.Thread(target=_tk_worker, daemon=True, name="tk-popup")
_thread.start()

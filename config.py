# ──────────────────────────────────────────────
# config.py  —  tweak everything from one place
# ──────────────────────────────────────────────

# Groq settings
GROQ_API_KEY = "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"
GROQ_MODEL   = "qwen/qwen3.8-27b"   # strong at math & reasoning, confirmed available

# Hotkeys
HOTKEY   = "ctrl+space"
EXIT_KEY = "esc"

# Popup
POPUP_WIDTH   = 540
POPUP_HEIGHT  = 220
POPUP_MARGIN  = 18          # px from screen edge
POPUP_SECONDS = 8           # auto-close after this many seconds (under 10s quiz timer)
POPUP_CORNER  = "top-right" # options: top-right | top-left | bottom-right | bottom-left

# Screen crop — cut out browser chrome & taskbar so OCR only reads page content
# Increase CROP_TOP if tabs/address bar/bookmarks are still being read
# Increase CROP_BOTTOM if taskbar noise appears
CROP_TOP    = 90    # px — skips tabs + address bar + bookmarks bar
CROP_BOTTOM = 50    # px — skips Windows taskbar
CROP_LEFT   = 0     # usually fine to leave at 0
CROP_RIGHT  = 0     # usually fine to leave at 0

# Misc
COOLDOWN = 0.8   # seconds to ignore repeated hotkey presses

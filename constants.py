"""
Akeno Downloader - shared constants.
Keep UI, quality, and branding values here so they are easy to find and change.
"""

from config_manager import APP_BASE_DIR, BUNDLE_DIR
import os

# =============================================================================
# SECTION: Branding & Assets
# =============================================================================
APP_NAME = "Akeno Downloader"
APP_VERSION = "1.2"
BUILD_LABEL = "SenpaiRato_V1.2"
COFFEE_URL = "https://www.coffeebede.com/senpairato"

# Bundled inside the exe (Res/). User files (ffmpeg, cookies) stay next to the exe.
LOGO_PATH = os.path.join(BUNDLE_DIR, "Res", "logo.png")
ICON_PATH = os.path.join(BUNDLE_DIR, "Res", "icon.ico")

# =============================================================================
# SECTION: Window Layout
# =============================================================================
WINDOW_TITLE = f"🎥 {APP_NAME}"
WINDOW_SIZE = "700x650"
FONT_FAMILY = "Segoe UI"

# =============================================================================
# SECTION: Download Quality Options
# =============================================================================
AVAILABLE_QUALITIES = (1080, 720, 480)

QUALITY_COLORS = {
    1080: "#1e88e5",
    720: "#4caf50",
    480: "#f44336",
}

# =============================================================================
# SECTION: UI Theme Colors
# =============================================================================
COLOR_READY = "green"
COLOR_BUSY = "yellow"
COLOR_ERROR = "red"
COLOR_CANCEL = "orange"
COLOR_PROGRESS = "#32CD32"
COLOR_COFFEE = "#FFA500"
COLOR_COFFEE_HOVER = "#FF8C00"

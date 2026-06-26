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
APP_VERSION = "2.0"
BUILD_LABEL = "SenpaiRato_V2.0"
COFFEE_URL = "https://www.coffeebede.com/senpairato"

LOGO_PATH = os.path.join(BUNDLE_DIR, "Res", "logo.png")
ICON_PATH = os.path.join(BUNDLE_DIR, "Res", "icon.ico")

# =============================================================================
# SECTION: Window Layout
# =============================================================================
WINDOW_TITLE = f"{APP_NAME}"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 700

# =============================================================================
# SECTION: Download Quality Options
# =============================================================================
AVAILABLE_QUALITIES = (2160, 1080, 720, 480)
QUALITY_LABELS = {
    2160: "4K (2160p)",
    1080: "Full HD (1080p)",
    720: "HD (720p)",
    480: "SD (480p)",
}
QUALITY_COLORS = {
    2160: "#8b5cf6",
    1080: "#c97832",
    720: "#5a9e6f",
    480: "#8b7355",
}

"""
Akeno Downloader - paths and user settings.
All file paths are relative to the application folder (works for script + .exe builds).
"""

import json
import os
import sys
from typing import Any, Dict

# =============================================================================
# SECTION: Application Paths
# =============================================================================
if getattr(sys, "frozen", False):
    APP_BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, "_MEIPASS", APP_BASE_DIR)
else:
    APP_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_BASE_DIR

DOWNLOAD_DIR = os.path.join(APP_BASE_DIR, "YouTube_Downloads")
VIDEO_DIR = os.path.join(DOWNLOAD_DIR, "Videos")

COOKIE_FILE_PATH = os.path.join(APP_BASE_DIR, "cookies.txt")
FFMPEG_PATH = os.path.join(APP_BASE_DIR, "ffmpeg.exe")
CONFIG_FILE = os.path.join(APP_BASE_DIR, "config.json")

LEGACY_PATH_MARKERS = ("AkenoDownloader v1.0",)


# =============================================================================
# SECTION: Directory Setup
# =============================================================================
def ensure_directories() -> None:
    """Create download folders if they do not exist."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)


# =============================================================================
# SECTION: Config Load / Save
# =============================================================================
def _default_config() -> Dict[str, Any]:
    return {
        "theme": "dark",
        "download_dir": DOWNLOAD_DIR,
    }


def _resolve_download_dir(configured_path: str) -> str:
    """Use a valid download folder and migrate away from old hard-coded paths."""
    if not configured_path:
        return DOWNLOAD_DIR

    if any(marker in configured_path for marker in LEGACY_PATH_MARKERS):
        return DOWNLOAD_DIR

    if not os.path.isabs(configured_path):
        configured_path = os.path.join(APP_BASE_DIR, configured_path)

    if os.path.isdir(configured_path):
        return configured_path

    return DOWNLOAD_DIR


def load_config() -> Dict[str, Any]:
    """Load settings from config.json."""
    config = _default_config()

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
                stored = json.load(config_file)
                config.update(stored)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error loading settings: {error}")

    config["download_dir"] = _resolve_download_dir(config.get("download_dir", DOWNLOAD_DIR))
    config.setdefault("theme", "dark")
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save settings to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
    except OSError as error:
        print(f"Error saving settings: {error}")

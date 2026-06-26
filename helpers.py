"""
Akeno Downloader - general helper utilities.
"""

import os
import re
from typing import List, Union

from config_manager import COOKIE_FILE_PATH, FFMPEG_PATH


# =============================================================================
# SECTION: Startup Checks
# =============================================================================
def check_dependencies() -> List[str]:
    """Check for required files before the GUI starts."""
    errors = []

    if not os.path.exists(FFMPEG_PATH):
        errors.append(
            f"FFmpeg not found: {FFMPEG_PATH}\n"
            "Please place ffmpeg.exe next to the program."
        )

    return errors


# =============================================================================
# SECTION: Formatting
# =============================================================================
def format_bytes(bytes_value: Union[int, float]) -> str:
    """Format bytes to a human-readable string."""
    if bytes_value is None or bytes_value == 0:
        return "0.00 B"

    value = float(bytes_value)
    for unit in ("B", "KB", "MB", "GB"):
        if abs(value) < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} TB"


def sanitize_filename(title: str) -> str:
    """Remove characters that are invalid in Windows file names."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", title)

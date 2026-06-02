"""
Akeno Downloader - YouTube cookie handling.
Supports Netscape format and Cookie-Editor #HttpOnly_ exports.
"""

import os
from typing import Optional, Set, Tuple, Union

from config_manager import APP_BASE_DIR, COOKIE_FILE_PATH

# =============================================================================
# SECTION: Cookie Validation
# =============================================================================
HTTPONLY_COOKIE_PREFIX = "#HttpOnly_"

YOUTUBE_AUTH_COOKIE_NAMES = frozenset({
    "SID", "HSID", "SSID", "APISID", "SAPISID", "LOGIN_INFO",
    "__Secure-1PSID", "__Secure-3PSID",
    "__Secure-1PAPISID", "__Secure-3PAPISID",
})

NETSCAPE_HEADERS = {"# Netscape HTTP Cookie File", "# HTTP Cookie File"}


def _parse_cookie_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse one Netscape cookie line, including Cookie-Editor HttpOnly exports."""
    if not line or not line.strip():
        return None

    working_line = line
    if working_line.startswith(HTTPONLY_COOKIE_PREFIX):
        working_line = working_line[len(HTTPONLY_COOKIE_PREFIX):]
    elif working_line.startswith("#"):
        return None

    parts = working_line.split("\t")
    if len(parts) < 7:
        return None

    return parts[0], parts[5]


def is_cookie_file_usable(cookie_path: str = COOKIE_FILE_PATH) -> bool:
    """Return True when cookies.txt exists and contains YouTube auth cookies."""
    if not cookie_path or not os.path.isfile(cookie_path):
        return False

    try:
        with open(cookie_path, "r", encoding="utf-8", errors="ignore") as cookie_file:
            content = cookie_file.read().strip()
    except OSError:
        return False

    if not content:
        return False

    if content.splitlines()[0].strip() not in NETSCAPE_HEADERS:
        return False

    found_names = _collect_youtube_cookie_names(content)
    return bool(found_names & YOUTUBE_AUTH_COOKIE_NAMES)


def _collect_youtube_cookie_names(content: str) -> Set[str]:
    found_names: Set[str] = set()
    for line in content.splitlines():
        parsed = _parse_cookie_line(line)
        if not parsed:
            continue
        domain, cookie_name = parsed
        if "youtube.com" in domain.lower():
            found_names.add(cookie_name)
    return found_names


# =============================================================================
# SECTION: Cookie Normalization (Cookie-Editor -> yt-dlp)
# =============================================================================
def normalize_cookie_file(source_path: str, destination_path: str) -> str:
    """Convert browser exports into a yt-dlp-friendly Netscape cookie file."""
    with open(source_path, "r", encoding="utf-8", errors="ignore") as source_file:
        lines = source_file.read().splitlines()

    normalized_lines = ["# Netscape HTTP Cookie File"]
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in NETSCAPE_HEADERS:
            continue
        if stripped.startswith("#") and not stripped.startswith(HTTPONLY_COOKIE_PREFIX):
            normalized_lines.append(stripped)
            continue

        parsed = _parse_cookie_line(stripped)
        if not parsed:
            continue

        working_line = stripped
        if working_line.startswith(HTTPONLY_COOKIE_PREFIX):
            working_line = working_line[len(HTTPONLY_COOKIE_PREFIX):]
        normalized_lines.append(working_line)

    with open(destination_path, "w", encoding="utf-8", newline="\n") as destination_file:
        destination_file.write("\n".join(normalized_lines) + "\n")

    return destination_path


def get_ytdlp_cookie_file(source_path: str = COOKIE_FILE_PATH) -> Optional[str]:
    """Return a normalized cookie file path ready for yt-dlp."""
    if not is_cookie_file_usable(source_path):
        return None

    normalized_path = os.path.join(APP_BASE_DIR, ".cookies_ytdlp.txt")
    try:
        source_mtime = os.path.getmtime(source_path)
        if (
            os.path.isfile(normalized_path)
            and os.path.getmtime(normalized_path) >= source_mtime
        ):
            return normalized_path
        normalize_cookie_file(source_path, normalized_path)
        return normalized_path
    except OSError:
        return source_path


# =============================================================================
# SECTION: Error Detection
# =============================================================================
def is_auth_related_error(error: Union[Exception, str]) -> bool:
    """Detect cookie/login/bot-check failures from yt-dlp."""
    message = str(error).lower()
    keywords = (
        "cookie",
        "sign in",
        "not a bot",
        "authentication",
        "login required",
        "use --cookies",
        "cookies-from-browser",
    )
    return any(keyword in message for keyword in keywords)

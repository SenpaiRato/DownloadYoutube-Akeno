"""
Akeno Downloader - network helpers.
Auto-detects Windows/VPN system proxy and available JS runtimes for yt-dlp.
"""

import shutil
import subprocess
import sys
import urllib.request
from typing import Optional


# =============================================================================
# SECTION: System Proxy Detection
# =============================================================================
def _normalize_proxy_url(proxy_value: str) -> Optional[str]:
    proxy_value = proxy_value.strip()
    if not proxy_value or proxy_value.lower() in {"direct", "(direct)"}:
        return None

    if ";" in proxy_value:
        parts = {}
        for segment in proxy_value.split(";"):
            if "=" in segment:
                scheme, address = segment.split("=", 1)
                parts[scheme.strip().lower()] = address.strip()
            elif segment.strip():
                parts["http"] = segment.strip()
        proxy_value = parts.get("https") or parts.get("http") or next(iter(parts.values()), "")

    if not proxy_value:
        return None
    if "://" not in proxy_value:
        proxy_value = f"http://{proxy_value}"
    return proxy_value


def _read_windows_ie_proxy() -> Optional[str]:
    if sys.platform != "win32":
        return None

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        ) as key:
            enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            if not enabled:
                return None
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            return _normalize_proxy_url(str(proxy_server))
    except OSError:
        return None


def _read_winhttp_proxy() -> Optional[str]:
    if sys.platform != "win32":
        return None

    try:
        result = subprocess.run(
            ["netsh", "winhttp", "show", "proxy"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.lower().startswith("proxy server"):
            _, _, value = line.partition(":")
            return _normalize_proxy_url(value)
    return None


def get_system_proxy() -> Optional[str]:
    """
    Detect the Windows/VPN/system proxy.
    Returns None when no proxy is configured (direct connection).
    """
    proxies = urllib.request.getproxies()
    for key in ("https", "http", "all"):
        proxy = proxies.get(key)
        if proxy:
            normalized = _normalize_proxy_url(proxy)
            if normalized:
                return normalized

    for reader in (_read_windows_ie_proxy, _read_winhttp_proxy):
        proxy = reader()
        if proxy:
            return proxy

    return None


# =============================================================================
# SECTION: yt-dlp JavaScript Runtimes
# =============================================================================
def detect_js_runtimes() -> dict:
    """Enable installed JS runtimes required by modern yt-dlp YouTube extraction."""
    runtimes = {"deno": {}}

    for runtime_name in ("node", "deno", "bun"):
        runtime_path = shutil.which(runtime_name)
        if runtime_path:
            runtimes[runtime_name] = {"path": runtime_path}

    return runtimes

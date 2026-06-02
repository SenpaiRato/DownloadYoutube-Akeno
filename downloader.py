"""
Akeno Downloader - yt-dlp download engine.
Handles video info extraction and quality-based downloads.
"""

import os
import threading
from typing import Any, Callable, Dict, Optional

import yt_dlp

from config_manager import FFMPEG_PATH, VIDEO_DIR
from cookies import get_ytdlp_cookie_file
from exceptions import DownloadCanceledException
from network import detect_js_runtimes, get_system_proxy


class DownloadManager:
    """Wraps yt-dlp with proxy, cookie, and cancellation support."""

    def __init__(
        self,
        progress_hook: Callable[[Dict[str, Any]], None],
        cancel_event: threading.Event,
    ):
        self.progress_hook = progress_hook
        self._download_canceled = cancel_event
        self.current_download_process: Optional[yt_dlp.YoutubeDL] = None

    # =========================================================================
    # SECTION: Network
    # =========================================================================
    @staticmethod
    def detect_proxy() -> Optional[str]:
        """Backward-compatible alias for system proxy detection."""
        return get_system_proxy()

    # =========================================================================
    # SECTION: Progress & Cancellation
    # =========================================================================
    def _wrapped_progress_hook(self, status: Dict[str, Any]) -> None:
        if self._download_canceled.is_set():
            raise DownloadCanceledException("Download canceled by user.")
        self.progress_hook(status)

    # =========================================================================
    # SECTION: yt-dlp Options
    # =========================================================================
    @staticmethod
    def _video_format(resolution: int) -> str:
        return (
            f"bv*[height<={resolution}][ext=mp4]+ba[ext=m4a]/"
            f"bv*[height<={resolution}]+ba/b[height<={resolution}]/best"
        )

    def _build_ydl_opts(
        self,
        *,
        download: bool,
        resolution: Optional[int] = None,
        output_template: Optional[str] = None,
    ) -> Dict[str, Any]:
        cookie_file = get_ytdlp_cookie_file()

        opts: Dict[str, Any] = {
            "quiet": not download,
            "no_warnings": not download,
            "skip_download": not download,
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
            "nocheckcertificate": True,
            "js_runtimes": detect_js_runtimes(),
            "extractor_args": {
                "youtube": {
                    "player_client": (
                        ["web", "tv", "ios"] if cookie_file else ["web", "android"]
                    ),
                }
            },
        }

        if download:
            opts["progress_hooks"] = [self._wrapped_progress_hook]
            opts["merge_output_format"] = "mp4"
            if output_template:
                opts["outtmpl"] = output_template
            if resolution is not None:
                opts["format"] = self._video_format(resolution)
        else:
            opts["format"] = "best[ext=mp4]/best"

        if os.path.isfile(FFMPEG_PATH):
            opts["ffmpeg_location"] = FFMPEG_PATH

        if cookie_file:
            opts["cookiefile"] = cookie_file

        proxy = get_system_proxy()
        if proxy:
            opts["proxy"] = proxy

        return opts

    # =========================================================================
    # SECTION: Public API
    # =========================================================================
    def fetch_video_info(self, url: str) -> Dict[str, Any]:
        """Fetch video metadata using the same settings as downloads."""
        ydl_opts = self._build_ydl_opts(download=False)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise yt_dlp.DownloadError("Could not extract video information.")

        if info.get("_type") == "playlist" and info.get("entries"):
            return next(entry for entry in info["entries"] if entry)

        return info

    def start_download(self, info: Dict[str, Any], resolution: int, filename: str) -> None:
        """Download the selected video quality."""
        target_url = info.get("webpage_url") or info.get("original_url") or info.get("url")
        if not target_url:
            raise ValueError("Video URL is missing from extracted info.")

        output_template = os.path.join(VIDEO_DIR, f"{filename}.%(ext)s")
        ydl_opts = self._build_ydl_opts(
            download=True,
            resolution=resolution,
            output_template=output_template,
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.current_download_process = ydl
                ydl.download([target_url])

            if self._download_canceled.is_set():
                raise DownloadCanceledException("Download canceled by user.")
        except DownloadCanceledException:
            raise
        finally:
            self.current_download_process = None

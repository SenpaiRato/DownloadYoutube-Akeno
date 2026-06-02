"""
Akeno Downloader - main GUI window.
Built with CustomTkinter; download logic lives in downloader.py.
"""

import os
import subprocess
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox
from typing import Any, Dict

import customtkinter as ctk
import yt_dlp
from PIL import Image

from config_manager import ensure_directories, load_config, save_config
from constants import (
    APP_NAME,
    AVAILABLE_QUALITIES,
    COFFEE_URL,
    BUILD_LABEL,
    COLOR_BUSY,
    COLOR_CANCEL,
    COLOR_COFFEE,
    COLOR_COFFEE_HOVER,
    COLOR_ERROR,
    COLOR_PROGRESS,
    COLOR_READY,
    FONT_FAMILY,
    ICON_PATH,
    LOGO_PATH,
    QUALITY_COLORS,
    WINDOW_SIZE,
    WINDOW_TITLE,
)
from cookies import is_auth_related_error
from downloader import DownloadManager
from exceptions import DownloadCanceledException
from helpers import check_dependencies, format_bytes, sanitize_filename
from network import get_system_proxy

ctk.set_default_color_theme("blue")


class YouTubeDownloader(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # =====================================================================
        # SECTION: Startup
        # =====================================================================
        self.config = load_config()
        ctk.set_appearance_mode(self.config.get("theme", "dark"))

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)

        self._download_canceled = threading.Event()
        self._is_downloading = False

        startup_errors = check_dependencies()
        if startup_errors:
            messagebox.showerror("Startup Error", "\n\n".join(startup_errors))

        ensure_directories()
        self._set_window_icon()
        self._build_ui()

    # =========================================================================
    # SECTION: UI Construction
    # =========================================================================
    def _set_window_icon(self) -> None:
        try:
            self.iconbitmap(ICON_PATH)
        except Exception as error:
            print(f"Could not load window icon: {error}")

    def _build_ui(self) -> None:
        self._build_header()
        self._build_input_area()
        self._build_selection_area()
        self._build_info_area()
        self._build_progress_area()
        self._build_bottom_actions()
        self._build_status_bar()

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=20, padx=40, fill="x")

        if os.path.exists(LOGO_PATH):
            try:
                logo_image = ctk.CTkImage(
                    light_image=Image.open(LOGO_PATH),
                    dark_image=Image.open(LOGO_PATH),
                    size=(50, 50),
                )
                ctk.CTkLabel(header_frame, text="", image=logo_image, width=50, height=50).pack(
                    side="left", padx=5
                )
            except Exception as error:
                print(f"Error loading logo: {error}")

        self.title_label = ctk.CTkLabel(
            header_frame,
            text=APP_NAME,
            font=(FONT_FAMILY, 16, "bold"),
            text_color="white" if ctk.get_appearance_mode() == "Dark" else "black",
        )
        self.title_label.pack(side="left", padx=10)

        ctk.CTkButton(
            header_frame,
            text="☕ Buy Me a Coffee",
            font=(FONT_FAMILY, 12, "bold"),
            width=200,
            height=40,
            command=self.open_coffee_page,
            fg_color=COLOR_COFFEE,
            hover_color=COLOR_COFFEE_HOVER,
            text_color="black",
        ).pack(side="left", padx=5)

        self.mode_button = ctk.CTkButton(
            header_frame,
            text="☀️ Light Mode" if self.config.get("theme", "dark") == "dark" else "🌙 Dark Mode",
            width=120,
            font=(FONT_FAMILY, 10),
            command=self.toggle_mode,
        )
        self.mode_button.pack(side="right")

    def _build_input_area(self) -> None:
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, padx=40, fill="x")

        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Paste YouTube URL here...",
            font=(FONT_FAMILY, 12),
            height=40,
        )
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.download_btn = ctk.CTkButton(
            input_frame,
            text="⬇️ Download",
            width=120,
            font=(FONT_FAMILY, 12, "bold"),
            command=self.ask_format,
        )
        self.download_btn.pack(side="left", padx=5)

    def _build_selection_area(self) -> None:
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.pack(pady=10, padx=40, fill="x")
        self.reset_selection_frame()

    def _build_info_area(self) -> None:
        info_frame = ctk.CTkFrame(self, corner_radius=10)
        info_frame.pack(pady=15, padx=40, fill="x")

        self.title_label_info = ctk.CTkLabel(
            info_frame,
            text="No video loaded",
            font=(FONT_FAMILY, 14),
            wraplength=600,
        )
        self.title_label_info.pack(pady=5)

    def _build_progress_area(self) -> None:
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=COLOR_PROGRESS)
        self.progress_bar.pack(pady=20)

        self.download_info_label = ctk.CTkLabel(
            self,
            text="0.0 MB / 0.0 MB | 0%",
            text_color="white",
            font=(FONT_FAMILY, 10),
            anchor="center",
        )
        self.download_info_label.pack(pady=5)

        self.speed_label = ctk.CTkLabel(
            self,
            text="Speed: - | ETA: -",
            text_color="gray",
            font=(FONT_FAMILY, 12),
        )
        self.speed_label.pack()

    def _build_bottom_actions(self) -> None:
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)

        self.open_folder_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Open Folder",
            font=(FONT_FAMILY, 12, "bold"),
            width=120,
            height=40,
            command=self.open_download_folder,
        )
        self.open_folder_btn.pack(side="left", padx=10)

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear All",
            font=(FONT_FAMILY, 14, "bold"),
            width=150,
            height=40,
            command=self.clear_all,
        )
        self.clear_btn.pack(side="left", padx=10)

    def _build_status_bar(self) -> None:
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            text_color=COLOR_READY,
            font=(FONT_FAMILY, 16, "bold"),
            anchor="center",
        )
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

        ctk.CTkLabel(
            self,
            text=BUILD_LABEL,
            font=(FONT_FAMILY, 9),
            text_color="#666666",
            anchor="e",
        ).place(relx=0.98, rely=0.99, anchor="se")

    # =========================================================================
    # SECTION: UI State Helpers
    # =========================================================================
    def reset_selection_frame(self) -> None:
        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        self.selection_label = ctk.CTkLabel(
            self.selection_frame,
            text="Enter URL and click Download to start",
            text_color="gray",
            font=(FONT_FAMILY, 12),
        )
        self.selection_label.pack(pady=20)

    def reset_info(self) -> None:
        self.title_label_info.configure(text="No video loaded")

    def reset_progress(self) -> None:
        self.progress_bar.set(0)
        self.speed_label.configure(text="Speed: - | ETA: -")
        self.download_info_label.configure(text="0.0 MB / 0.0 MB | 0%")

    def set_ui_state(self, state: str) -> None:
        self.url_entry.configure(state=state)
        self.download_btn.configure(state=state)
        self.clear_btn.configure(state=state)

        for child in self.selection_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for button in child.winfo_children():
                    if isinstance(button, ctk.CTkButton):
                        button.configure(state=state)

    def show_error(self, message: str) -> None:
        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.selection_frame,
            text=f"Error: {message}",
            text_color=COLOR_ERROR,
            font=(FONT_FAMILY, 12),
        ).pack(pady=20)

        self.set_ui_state("normal")
        self.status_label.configure(text="Error occurred.", text_color=COLOR_ERROR)

    # =========================================================================
    # SECTION: User Actions
    # =========================================================================
    def open_download_folder(self) -> None:
        download_dir = self.config.get("download_dir")
        try:
            os.startfile(download_dir)
        except OSError:
            for opener in (["xdg-open", download_dir], ["open", download_dir]):
                try:
                    subprocess.Popen(opener)
                    return
                except OSError:
                    continue
            messagebox.showerror("Error", "Could not open folder. Please check manually.")

    def show_cookie_warning(self) -> None:
        proxy = get_system_proxy()
        proxy_line = (
            f"\n\nActive proxy: {proxy}"
            if proxy
            else "\n\nNo system proxy detected (direct connection)."
        )
        messagebox.showwarning(
            "Cookie / Login Required",
            (
                "YouTube rejected the current session.\n\n"
                "1. Open your browser while logged into YouTube.\n"
                "2. Export cookies to cookies.txt next to this program.\n"
                "3. Cookie-Editor / Netscape format is supported (#HttpOnly_ lines too).\n"
                "4. Make sure LOGIN_INFO and __Secure-1PSID are included.\n"
                "5. Replace the old cookies.txt and try again."
                f"{proxy_line}"
            ),
        )

    def toggle_mode(self) -> None:
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.mode_button.configure(text="🌙 Dark Mode")
            self.config["theme"] = "light"
        else:
            ctk.set_appearance_mode("Dark")
            self.mode_button.configure(text="☀️ Light Mode")
            self.config["theme"] = "dark"

        self.title_label.configure(
            text_color="white" if ctk.get_appearance_mode() == "Dark" else "black"
        )
        save_config(self.config)

    def clear_all(self) -> None:
        if self._is_downloading:
            self._download_canceled.set()
            self.status_label.configure(text="Cancelling download...", text_color=COLOR_CANCEL)
            return

        self._download_canceled.clear()
        self.url_entry.delete(0, tk.END)
        self.reset_selection_frame()
        self.reset_info()
        self.reset_progress()
        self.status_label.configure(text="Ready", text_color=COLOR_READY)
        self.set_ui_state("normal")

    def open_coffee_page(self) -> None:
        webbrowser.open(COFFEE_URL)

    # =========================================================================
    # SECTION: Fetch Video Info
    # =========================================================================
    def ask_format(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return

        self.set_ui_state("disabled")
        self.status_label.configure(text="Fetching video info...", text_color=COLOR_BUSY)
        self.reset_progress()

        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.selection_frame,
            text="Fetching video info...",
            font=(FONT_FAMILY, 12),
        ).pack(pady=20)

        threading.Thread(target=self.fetch_video_info_for_quality, args=(url,), daemon=True).start()

    def fetch_video_info_for_quality(self, url: str) -> None:
        try:
            manager = DownloadManager(progress_hook=lambda _: None, cancel_event=threading.Event())
            info = manager.fetch_video_info(url)
            title = sanitize_filename(info["title"])

            self.after(
                0,
                lambda: self.title_label_info.configure(
                    text=f"{title[:60]}..." if len(title) > 60 else title
                ),
            )
            self.after(0, lambda: self.show_quality_options(info))

        except Exception as error:
            self.after(0, lambda: self._handle_fetch_error(error))

    def _handle_fetch_error(self, error: Exception) -> None:
        if is_auth_related_error(error):
            self.show_cookie_warning()
            self.show_error("YouTube login verification failed. Refresh cookies.txt.")
            return

        error_text = str(error).lower()
        if "signature" in error_text or ("format" in error_text and "not available" in error_text):
            self.show_error(
                "YouTube signature verification failed.\n"
                "Update yt-dlp (pip install -U yt-dlp) and try again."
            )
            return

        self.show_error(str(error))

    def show_quality_options(self, info: Dict[str, Any]) -> None:
        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.selection_frame,
            text="Select Video Quality:",
            font=(FONT_FAMILY, 16, "bold"),
        ).pack(pady=10)

        btn_frame = ctk.CTkFrame(self.selection_frame)
        btn_frame.pack(pady=10)

        for resolution in AVAILABLE_QUALITIES:
            ctk.CTkButton(
                btn_frame,
                text=f"{resolution}p",
                width=120,
                height=50,
                font=(FONT_FAMILY, 14, "bold"),
                fg_color=QUALITY_COLORS[resolution],
                hover_color=QUALITY_COLORS[resolution],
                command=lambda r=resolution, i=info: self.start_download_thread(i, r),
            ).pack(side="left", padx=5)

    # =========================================================================
    # SECTION: Download Flow
    # =========================================================================
    def start_download_thread(self, info: Dict[str, Any], resolution: int) -> None:
        self.set_ui_state("disabled")
        self._is_downloading = True
        self.reset_selection_frame()

        title = sanitize_filename(info["title"])
        filename = f"{title}_{resolution}p"
        self.status_label.configure(text="Starting download...", text_color=COLOR_BUSY)

        manager = DownloadManager(
            progress_hook=self.progress_hook,
            cancel_event=self._download_canceled,
        )
        threading.Thread(
            target=self.run_download,
            args=(manager, info, resolution, filename),
            daemon=True,
        ).start()

    def run_download(
        self,
        download_manager: DownloadManager,
        info: Dict[str, Any],
        resolution: int,
        filename: str,
    ) -> None:
        try:
            download_manager.start_download(info, resolution, filename)
            if self._download_canceled.is_set():
                self._set_status("Download canceled.", COLOR_ERROR)
            else:
                self._set_status("Download completed successfully!", COLOR_READY)
        except DownloadCanceledException:
            self._set_status("Download canceled.", COLOR_ERROR)
        except yt_dlp.DownloadError as error:
            if is_auth_related_error(error):
                self.after(0, self.show_cookie_warning)
                self._set_status("Download failed.", COLOR_ERROR)
            else:
                error_text = str(error)
                self.after(0, lambda: messagebox.showerror("Download Failed", error_text))
                self._set_status("Download failed.", COLOR_ERROR)
        except Exception as error:
            error_text = str(error)
            self.after(0, lambda: messagebox.showerror("Download Failed", error_text))
            self._set_status("Download failed.", COLOR_ERROR)
        finally:
            self._is_downloading = False
            self._download_canceled.clear()
            self.after(0, lambda: self.set_ui_state("normal"))

    def _set_status(self, text: str, color: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    # =========================================================================
    # SECTION: Download Progress Hook
    # =========================================================================
    def progress_hook(self, status: Dict[str, Any]) -> None:
        if self._download_canceled.is_set():
            raise DownloadCanceledException("Download canceled by user.")

        if not status or not isinstance(status, dict):
            return

        if status.get("status") == "downloading":
            total = (
                status.get("total_bytes_estimate")
                or status.get("total_bytes")
                or status.get("_total_bytes_estimate")
                or 1
            )
            downloaded = status.get("downloaded_bytes") or 0
            speed = status.get("speed") or 0
            eta = status.get("eta") or 0
            percent = downloaded / total if total > 0 else 0

            speed_str = f"{format_bytes(speed)}/s" if speed else "N/A"
            eta_str = f"{int(eta)}s" if eta else "?"

            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)

            self.after(
                0,
                lambda: self.download_info_label.configure(
                    text=f"{downloaded_mb:.2f} MB / {total_mb:.2f} MB | {percent:.1%}"
                ),
            )
            self.after(0, lambda: self.progress_bar.set(percent))
            self.after(
                0,
                lambda: self.speed_label.configure(text=f"Speed: {speed_str} | ETA: {eta_str}"),
            )

        elif status.get("status") == "finished":
            if self._download_canceled.is_set():
                self._set_status("Download canceled.", COLOR_ERROR)
            else:
                self.after(0, self.reset_progress)
                self._set_status("Download finished, processing...", COLOR_BUSY)

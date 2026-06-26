"""
Akeno Downloader v2.0 - PySide6 GUI.
Professional tabbed interface with downloader, cookies manager, and settings.
"""

import os
import subprocess
import threading
import webbrowser
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QProgressBar,
    QTextEdit,
    QGroupBox,
    QComboBox,
    QMessageBox,
    QFrame,
    QFileDialog,
    QSizePolicy,
    QSpacerItem,
)

from config_manager import (
    COOKIE_FILE_PATH,
    DOWNLOAD_DIR,
    VIDEO_DIR,
    ensure_directories,
    load_config,
    save_config,
)
from constants import (
    APP_NAME,
    APP_VERSION,
    AVAILABLE_QUALITIES,
    BUILD_LABEL,
    COFFEE_URL,
    ICON_PATH,
    QUALITY_COLORS,
)
from cookies import (
    is_auth_related_error,
    is_cookie_file_usable,
    normalize_cookie_file,
)
from downloader import DownloadManager
from exceptions import DownloadCanceledException
from helpers import check_dependencies, format_bytes, sanitize_filename
from network import get_system_proxy


class FetchInfoThread(QThread):
    """Background thread for fetching video info without blocking the UI."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            manager = DownloadManager(
                progress_hook=lambda _: None,
                cancel_event=threading.Event(),
            )
            info = manager.fetch_video_info(self.url)
            self.finished.emit(info)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    """Background thread for downloading videos."""

    progress = Signal(dict)
    finished = Signal()
    error = Signal(str)
    status = Signal(str)

    def __init__(self, info: dict, resolution: int, filename: str, parent=None):
        super().__init__(parent)
        self.info = info
        self.resolution = resolution
        self.filename = filename
        self._canceled = threading.Event()

    def run(self):
        try:
            manager = DownloadManager(
                progress_hook=self._on_progress,
                cancel_event=self._canceled,
            )
            manager.start_download(self.info, self.resolution, self.filename)
            if self._canceled.is_set():
                self.status.emit("canceled")
            else:
                self.status.emit("done")
            self.finished.emit()
        except DownloadCanceledException:
            self.status.emit("canceled")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._canceled.set()

    def _on_progress(self, status_dict):
        self.progress.emit(status_dict)


class CookiesManagerWidget(QWidget):
    """Tab widget for managing YouTube cookies."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self._setup_ui()
        self._load_current_cookies()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Cookie Manager")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #c97832;")
        layout.addWidget(title)

        desc = QLabel(
            "Paste your YouTube cookies here in Netscape format. "
            "Export from your browser using the Cookie-Editor extension."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 12px; margin-bottom: 8px;")
        layout.addWidget(desc)

        status_group = QGroupBox("Cookie Status")
        status_layout = QHBoxLayout(status_group)
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        self.status_text = QLabel("Checking...")
        self.status_text.setFont(QFont("Segoe UI", 11))
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        layout.addWidget(status_group)

        self.cookie_text = QTextEdit()
        self.cookie_text.setPlaceholderText(
            "# Netscape HTTP Cookie File\n"
            ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tvalue...\n"
            ".youtube.com\tTRUE\t/\tTRUE\t0\tHSID\tvalue...\n"
            "..."
        )
        self.cookie_text.setMinimumHeight(220)
        layout.addWidget(self.cookie_text)

        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Cookies")
        self.save_btn.setObjectName("accentBtn")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._save_cookies)
        btn_layout.addWidget(self.save_btn)

        self.import_btn = QPushButton("Import from File")
        self.import_btn.setMinimumHeight(40)
        self.import_btn.clicked.connect(self._import_from_file)
        btn_layout.addWidget(self.import_btn)

        self.clear_btn = QPushButton("Clear Cookies")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self._clear_cookies)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        tips_group = QGroupBox("How to Export Cookies")
        tips_layout = QVBoxLayout(tips_group)
        tips = [
            "1. Install the 'Cookie-Editor' extension in your browser.",
            "2. Go to youtube.com and make sure you are logged in.",
            "3. Click the Cookie-Editor icon and select 'Export' > 'Netscape'.",
            "4. Paste the exported text into the text area above.",
            '5. Click "Save Cookies" to apply.',
        ]
        for tip in tips:
            lbl = QLabel(tip)
            lbl.setStyleSheet("font-size: 12px; padding: 2px 0;")
            tips_layout.addWidget(lbl)
        layout.addWidget(tips_group)

        layout.addStretch()

    def _load_current_cookies(self):
        try:
            if os.path.isfile(COOKIE_FILE_PATH):
                with open(COOKIE_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                self.cookie_text.setPlainText(content)
                self._update_status()
            else:
                self.cookie_text.setPlainText("")
                self._set_status(False, "No cookies.txt file found. Paste cookies and save.")
        except OSError:
            self._set_status(False, "Could not read cookies file.")

    def _update_status(self):
        usable = is_cookie_file_usable(COOKIE_FILE_PATH)
        if usable:
            self._set_status(True, "Cookies are valid and contain YouTube auth tokens.")
        else:
            self._set_status(False, "Cookies are missing or incomplete. YouTube auth cookies required.")

    def _set_status(self, ok: bool, text: str):
        pixmap = QPixmap(16, 16)
        if ok:
            pixmap.fill(Qt.GlobalColor.green)
            self.status_text.setStyleSheet("color: #5a9e6f; font-weight: bold;")
        else:
            pixmap.fill(Qt.GlobalColor.red)
            self.status_text.setStyleSheet("color: #c94444; font-weight: bold;")
        self.status_icon.setPixmap(pixmap)
        self.status_text.setText(text)

    def _save_cookies(self):
        content = self.cookie_text.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Empty", "Please paste your cookies first.")
            return

        try:
            with open(COOKIE_FILE_PATH, "w", encoding="utf-8", newline="\n") as f:
                f.write(content + "\n")

            ytdlp_path = os.path.join(
                os.path.dirname(COOKIE_FILE_PATH), ".cookies_ytdlp.txt"
            )
            normalize_cookie_file(COOKIE_FILE_PATH, ytdlp_path)

            self._update_status()
            QMessageBox.information(self, "Saved", "Cookies saved successfully!")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to save cookies:\n{e}")

    def _import_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Cookies",
            "",
            "Text Files (*.txt);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.cookie_text.setPlainText(content)
            self._save_cookies()
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")

    def _clear_cookies(self):
        reply = QMessageBox.question(
            self,
            "Clear Cookies",
            "Are you sure you want to delete all cookies?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cookie_text.clear()
            try:
                if os.path.isfile(COOKIE_FILE_PATH):
                    os.remove(COOKIE_FILE_PATH)
                ytdlp_path = os.path.join(
                    os.path.dirname(COOKIE_FILE_PATH), ".cookies_ytdlp.txt"
                )
                if os.path.isfile(ytdlp_path):
                    os.remove(ytdlp_path)
            except OSError:
                pass
            self._set_status(False, "No cookies.txt file found. Paste cookies and save.")


class SettingsWidget(QWidget):
    """Tab widget for application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #c97832;")
        layout.addWidget(title)

        appearance_group = QGroupBox("Appearance")
        appearance_layout = QHBoxLayout(appearance_group)
        appearance_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current = self.config.get("theme", "dark")
        self.theme_combo.setCurrentText(current.capitalize())
        self.theme_combo.currentTextChanged.connect(self._on_theme_change)
        appearance_layout.addWidget(self.theme_combo)
        appearance_layout.addStretch()
        layout.addWidget(appearance_group)

        download_group = QGroupBox("Download Directory")
        download_layout = QVBoxLayout(download_group)
        dir_row = QHBoxLayout()
        self.dir_label = QLabel(self.config.get("download_dir", DOWNLOAD_DIR))
        self.dir_label.setStyleSheet("font-size: 11px;")
        dir_row.addWidget(self.dir_label, 1)
        self.change_dir_btn = QPushButton("Change")
        self.change_dir_btn.clicked.connect(self._change_download_dir)
        dir_row.addWidget(self.change_dir_btn)
        download_layout.addLayout(dir_row)
        layout.addWidget(download_group)

        info_group = QGroupBox("Application Info")
        info_layout = QVBoxLayout(info_group)
        info_items = [
            f"Name: {APP_NAME}",
            f"Version: {APP_VERSION}",
            f"Build: {BUILD_LABEL}",
            f"Cookies: {COOKIE_FILE_PATH}",
            f"FFmpeg: {os.path.join(os.path.dirname(COOKIE_FILE_PATH), 'ffmpeg.exe')}",
            f"Proxy: {get_system_proxy() or 'None (direct)'}",
        ]
        for item in info_items:
            lbl = QLabel(item)
            lbl.setStyleSheet("font-size: 12px; padding: 2px 0;")
            info_layout.addWidget(lbl)
        layout.addWidget(info_group)

        layout.addStretch()

    def _on_theme_change(self, text):
        theme = text.lower()
        self.config["theme"] = theme
        save_config(self.config)
        app = QApplication.instance()
        if app:
            if theme == "dark":
                app.setStyleSheet(self._dark_theme())
            else:
                app.setStyleSheet(self._light_theme())
        QMessageBox.information(
            self,
            "Theme Changed",
            "Theme will be fully applied on next restart.",
        )

    def _change_download_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", self.config.get("download_dir", DOWNLOAD_DIR)
        )
        if directory:
            self.config["download_dir"] = directory
            save_config(self.config)
            self.dir_label.setText(directory)
            QMessageBox.information(self, "Saved", f"Download directory changed to:\n{directory}")

    @staticmethod
    def _dark_theme():
        from main import _dark_theme
        return _dark_theme()

    @staticmethod
    def _light_theme():
        from main import _light_theme
        return _light_theme()


class DownloaderWidget(QWidget):
    """Main downloader tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self._fetch_thread: Optional[FetchInfoThread] = None
        self._download_thread: Optional[DownloadThread] = None
        self._is_downloading = False
        self._fetched_info: Optional[dict] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()

        if os.path.exists(ICON_PATH):
            icon_label = QLabel()
            pixmap = QPixmap(ICON_PATH).scaled(
                36, 36, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
            header.addWidget(icon_label)

        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #c97832;")
        header.addWidget(title)
        header.addStretch()

        coffee_btn = QPushButton("Buy Me a Coffee")
        coffee_btn.setObjectName("coffeeBtn")
        coffee_btn.setMinimumSize(180, 36)
        coffee_btn.clicked.connect(lambda: webbrowser.open(COFFEE_URL))
        header.addWidget(coffee_btn)
        layout.addLayout(header)

        url_group = QGroupBox("Video URL")
        url_layout = QHBoxLayout(url_group)
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Paste YouTube URL here...")
        self.url_entry.setMinimumHeight(40)
        self.url_entry.returnPressed.connect(self._on_download_click)
        url_layout.addWidget(self.url_entry, 1)
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("accentBtn")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.setMinimumWidth(130)
        self.download_btn.clicked.connect(self._on_download_click)
        url_layout.addWidget(self.download_btn)
        layout.addWidget(url_group)

        self.video_info_label = QLabel("No video loaded")
        self.video_info_label.setWordWrap(True)
        self.video_info_label.setFont(QFont("Segoe UI", 12))
        self.video_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_info_label.setStyleSheet("padding: 8px;")
        layout.addWidget(self.video_info_label)

        self.quality_group = QGroupBox("Select Quality")
        self.quality_layout = QHBoxLayout(self.quality_group)
        self.quality_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._quality_buttons: Dict[int, QPushButton] = {}
        for res in AVAILABLE_QUALITIES:
            btn = QPushButton(f"{res}p")
            btn.setMinimumSize(120, 50)
            btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            btn.setStyleSheet(
                f"background: {QUALITY_COLORS[res]}; border-radius: 8px; color: white;"
            )
            btn.clicked.connect(lambda checked, r=res: self._on_quality_selected(r))
            self._quality_buttons[res] = btn
            self.quality_layout.addWidget(btn)
        self.quality_group.setVisible(False)
        layout.addWidget(self.quality_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(22)
        layout.addWidget(self.progress_bar)

        stats_row = QHBoxLayout()
        self.downloaded_label = QLabel("0.00 MB / 0.00 MB | 0%")
        self.downloaded_label.setFont(QFont("Segoe UI", 10))
        stats_row.addWidget(self.downloaded_label)
        self.speed_label = QLabel("Speed: - | ETA: -")
        self.speed_label.setFont(QFont("Segoe UI", 10))
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        stats_row.addWidget(self.speed_label)
        layout.addLayout(stats_row)

        btn_row = QHBoxLayout()
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.setMinimumHeight(38)
        self.open_folder_btn.clicked.connect(self._open_download_folder)
        btn_row.addWidget(self.open_folder_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setVisible(False)
        btn_row.addWidget(self.cancel_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(self.clear_btn)
        layout.addLayout(btn_row)

        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 6px;")
        layout.addWidget(self.status_label)

        build_lbl = QLabel(BUILD_LABEL)
        build_lbl.setFont(QFont("Segoe UI", 8))
        build_lbl.setStyleSheet("opacity: 0.5;")
        build_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(build_lbl)

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; padding: 6px;")

    def _set_buttons_enabled(self, enabled: bool):
        self.url_entry.setEnabled(enabled)
        self.download_btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)

    def _disable_quality_buttons(self):
        for btn in self._quality_buttons.values():
            btn.setEnabled(False)

    def _enable_quality_buttons(self):
        for btn in self._quality_buttons.values():
            btn.setEnabled(True)

    def _on_download_click(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL!")
            return

        if self._is_downloading:
            return

        self._fetched_info = None
        self._set_buttons_enabled(False)
        self._set_status("Fetching video info...", "#c97832")
        self.progress_bar.setValue(0)
        self.downloaded_label.setText("0.00 MB / 0.00 MB | 0%")
        self.speed_label.setText("Speed: - | ETA: -")
        self.quality_group.setVisible(False)
        self.video_info_label.setText("Fetching video info...")

        self._fetch_thread = FetchInfoThread(url, self)
        self._fetch_thread.finished.connect(self._on_fetch_done)
        self._fetch_thread.error.connect(self._on_fetch_error)
        self._fetch_thread.start()

    def _on_fetch_done(self, info: dict):
        self._fetched_info = info
        title = sanitize_filename(info.get("title", "Unknown"))
        display = title[:70] + "..." if len(title) > 70 else title
        self.video_info_label.setText(display)
        self.quality_group.setVisible(True)
        self._enable_quality_buttons()
        self._set_buttons_enabled(True)
        self._set_status("Select a quality to download", "#5a9e6f")

    def _on_fetch_error(self, error: str):
        if is_auth_related_error(error):
            self._show_cookie_warning()
            self._set_status("YouTube login verification failed. Check cookies.", "#c94444")
        else:
            self._set_status(f"Error: {error[:80]}", "#c94444")
        self.video_info_label.setText("Failed to fetch video info")
        self._set_buttons_enabled(True)

    def _on_quality_selected(self, resolution: int):
        if self._is_downloading:
            return

        if self._fetched_info is None:
            self._set_status("No video info available. Click Download first.", "#c94444")
            return

        self._is_downloading = True
        self._set_buttons_enabled(False)
        self._disable_quality_buttons()
        self.cancel_btn.setVisible(True)
        self._set_status("Starting download...", "#c97832")
        self.progress_bar.setValue(0)

        self._start_download(self._fetched_info, resolution)

    def _start_download(self, info: dict, resolution: int):
        title = sanitize_filename(info.get("title", "video"))
        filename = f"{title}_{resolution}p"

        self._download_thread = DownloadThread(info, resolution, filename, self)
        self._download_thread.progress.connect(self._on_progress)
        self._download_thread.status.connect(self._on_download_status)
        self._download_thread.error.connect(self._on_download_error)
        self._download_thread.start()

    def _on_progress(self, status: dict):
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
            percent = int(downloaded / total * 100) if total > 0 else 0

            speed_str = f"{format_bytes(speed)}/s" if speed else "N/A"
            eta_str = f"{int(eta)}s" if eta else "?"

            self.progress_bar.setValue(percent)
            self.downloaded_label.setText(
                f"{format_bytes(downloaded)} / {format_bytes(total)} | {percent}%"
            )
            self.speed_label.setText(f"Speed: {speed_str} | ETA: {eta_str}")

        elif status.get("status") == "finished":
            self._set_status("Download finished, processing...", "#c97832")

    def _on_download_status(self, status: str):
        self._is_downloading = False
        self._fetched_info = None
        self.cancel_btn.setVisible(False)
        self.quality_group.setVisible(False)
        self._set_buttons_enabled(True)

        if status == "done":
            self._set_status("Download completed successfully!", "#5a9e6f")
            self.progress_bar.setValue(100)
        elif status == "canceled":
            self._set_status("Download canceled.", "#c94444")
        else:
            self._set_status("Download completed.", "#5a9e6f")

    def _on_download_error(self, error: str):
        self._is_downloading = False
        self._fetched_info = None
        self.cancel_btn.setVisible(False)
        self.quality_group.setVisible(False)
        self._set_buttons_enabled(True)

        if is_auth_related_error(error):
            self._show_cookie_warning()
            self._set_status("Download failed. Check cookies.", "#c94444")
        else:
            QMessageBox.critical(self, "Download Failed", error)
            self._set_status("Download failed.", "#c94444")

    def _on_cancel(self):
        if self._download_thread and self._download_thread.isRunning():
            self._download_thread.cancel()
            self._set_status("Canceling download...", "#c97832")

    def _clear_all(self):
        if self._is_downloading:
            self._on_cancel()
            return

        self._fetched_info = None
        self.url_entry.clear()
        self.video_info_label.setText("No video loaded")
        self.quality_group.setVisible(False)
        self.progress_bar.setValue(0)
        self.downloaded_label.setText("0.00 MB / 0.00 MB | 0%")
        self.speed_label.setText("Speed: - | ETA: -")
        self._enable_quality_buttons()
        self._set_buttons_enabled(True)
        self._set_status("Ready", "#5a9e6f")

    def _open_download_folder(self):
        folder = self.config.get("download_dir", DOWNLOAD_DIR)
        try:
            os.startfile(folder)
        except OSError:
            for cmd in (["xdg-open", folder], ["open", folder]):
                try:
                    subprocess.Popen(cmd)
                    return
                except OSError:
                    continue
            QMessageBox.warning(self, "Error", "Could not open folder.")

    def _show_cookie_warning(self):
        proxy = get_system_proxy()
        proxy_line = f"\n\nActive proxy: {proxy}" if proxy else "\n\nNo system proxy detected."
        QMessageBox.warning(
            self,
            "Cookie / Login Required",
            (
                "YouTube rejected the current session.\n\n"
                "1. Go to the Cookies tab in this app.\n"
                "2. Export cookies from your browser using Cookie-Editor.\n"
                "3. Paste and save them there.\n"
                "4. Make sure LOGIN_INFO and __Secure-1PSID are included."
                f"{proxy_line}"
            ),
        )


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(780, 680)
        self.resize(820, 720)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 11))
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.downloader_tab = DownloaderWidget()
        self.cookies_tab = CookiesManagerWidget()
        self.settings_tab = SettingsWidget()

        self.tabs.addTab(self.downloader_tab, "Downloader")
        self.tabs.addTab(self.cookies_tab, "Cookies")
        self.tabs.addTab(self.settings_tab, "Settings")

        main_layout.addWidget(self.tabs)

        startup_errors = check_dependencies()
        if startup_errors:
            errors_text = "\n\n".join(startup_errors)
            QMessageBox.warning(self, "Startup Warnings", errors_text)

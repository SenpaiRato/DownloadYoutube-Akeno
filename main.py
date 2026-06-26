"""
Akeno Downloader v2.0
Entry point for the desktop application.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from gui import MainWindow
from constants import ICON_PATH
from config_manager import load_config


DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
}
QWidget {
    color: #dcdcdc;
    font-family: "Segoe UI";
    font-size: 13px;
}
QLabel {
    background: transparent;
}
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 9px 14px;
    color: #dcdcdc;
    selection-background-color: #c97832;
}
QLineEdit:focus {
    border: 1px solid #c97832;
}
QLineEdit:disabled {
    background-color: #333333;
    color: #666666;
}
QPushButton {
    background-color: #444444;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 9px 18px;
    color: #dcdcdc;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #c97832;
    border-color: #c97832;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #a86228;
    border-color: #a86228;
}
QPushButton:disabled {
    background-color: #353535;
    color: #555555;
    border-color: #3c3c3c;
}
QPushButton#accentBtn {
    background-color: #c97832;
    border: 1px solid #c97832;
    color: #ffffff;
}
QPushButton#accentBtn:hover {
    background-color: #d98a44;
    border-color: #d98a44;
}
QPushButton#coffeeBtn {
    background-color: #c97832;
    border: 1px solid #c97832;
    color: #ffffff;
}
QPushButton#coffeeBtn:hover {
    background-color: #d98a44;
    border-color: #d98a44;
}
QPushButton#cancelBtn {
    background-color: #b33a3a;
    border: 1px solid #b33a3a;
    color: #ffffff;
}
QPushButton#cancelBtn:hover {
    background-color: #c94444;
    border-color: #c94444;
}
QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 6px;
    text-align: center;
    color: #dcdcdc;
    min-height: 22px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #c97832, stop:1 #e0a060);
    border-radius: 5px;
}
QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 7px 12px;
    color: #dcdcdc;
}
QComboBox:hover {
    border: 1px solid #c97832;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    color: #dcdcdc;
    selection-background-color: #c97832;
}
QTabWidget::pane {
    border: 1px solid #555555;
    background-color: #2b2b2b;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #353535;
    color: #999999;
    padding: 10px 26px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #555555;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #2b2b2b;
    color: #c97832;
    border-color: #555555;
    border-bottom: 2px solid #c97832;
}
QTabBar::tab:hover:!selected {
    background-color: #404040;
    color: #dcdcdc;
}
QTextEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 10px;
    color: #dcdcdc;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
}
QTextEdit:focus {
    border: 1px solid #c97832;
}
QGroupBox {
    border: 1px solid #555555;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: bold;
    color: #c97832;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}
QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background-color: #c97832;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QToolTip {
    background-color: #3c3c3c;
    color: #dcdcdc;
    border: 1px solid #c97832;
    padding: 4px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f0ede8;
}
QWidget {
    color: #2c2c2c;
    font-family: "Segoe UI";
    font-size: 13px;
}
QLabel {
    background: transparent;
}
QLineEdit {
    background-color: #faf9f7;
    border: 1px solid #c8c4bc;
    border-radius: 6px;
    padding: 9px 14px;
    color: #2c2c2c;
    selection-background-color: #c97832;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border: 1px solid #c97832;
}
QLineEdit:disabled {
    background-color: #e8e6e1;
    color: #999999;
}
QPushButton {
    background-color: #e8e4dd;
    border: 1px solid #c8c4bc;
    border-radius: 6px;
    padding: 9px 18px;
    color: #4a4038;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #c97832;
    border-color: #c97832;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #a86228;
    border-color: #a86228;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: #e8e6e1;
    color: #aaaaaa;
    border-color: #d5d2cc;
}
QPushButton#accentBtn {
    background-color: #c97832;
    border: 1px solid #c97832;
    color: #ffffff;
}
QPushButton#accentBtn:hover {
    background-color: #d98a44;
    border-color: #d98a44;
}
QPushButton#coffeeBtn {
    background-color: #c97832;
    border: 1px solid #c97832;
    color: #ffffff;
}
QPushButton#coffeeBtn:hover {
    background-color: #d98a44;
    border-color: #d98a44;
}
QPushButton#cancelBtn {
    background-color: #b33a3a;
    border: 1px solid #b33a3a;
    color: #ffffff;
}
QPushButton#cancelBtn:hover {
    background-color: #c94444;
    border-color: #c94444;
}
QProgressBar {
    background-color: #e0ddd6;
    border: 1px solid #c8c4bc;
    border-radius: 6px;
    text-align: center;
    color: #4a4038;
    min-height: 22px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #c97832, stop:1 #e0a060);
    border-radius: 5px;
}
QComboBox {
    background-color: #faf9f7;
    border: 1px solid #c8c4bc;
    border-radius: 6px;
    padding: 7px 12px;
    color: #2c2c2c;
}
QComboBox:hover {
    border: 1px solid #c97832;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #faf9f7;
    border: 1px solid #c8c4bc;
    color: #2c2c2c;
    selection-background-color: #c97832;
    selection-color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #c8c4bc;
    background-color: #f0ede8;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #e0ddd6;
    color: #7a7268;
    padding: 10px 26px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #c8c4bc;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #f0ede8;
    color: #c97832;
    border-color: #c8c4bc;
    border-bottom: 2px solid #c97832;
}
QTabBar::tab:hover:!selected {
    background-color: #e8e4dd;
    color: #4a4038;
}
QTextEdit {
    background-color: #faf9f7;
    border: 1px solid #c8c4bc;
    border-radius: 6px;
    padding: 10px;
    color: #2c2c2c;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
}
QTextEdit:focus {
    border: 1px solid #c97832;
}
QGroupBox {
    border: 1px solid #c8c4bc;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: bold;
    color: #a06228;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}
QScrollBar:vertical {
    background-color: #f0ede8;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #c8c4bc;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background-color: #c97832;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QToolTip {
    background-color: #faf9f7;
    color: #2c2c2c;
    border: 1px solid #c97832;
    padding: 4px;
}
"""


def _dark_theme():
    return DARK_THEME


def _light_theme():
    return LIGHT_THEME


def main() -> None:
    config = load_config()
    app = QApplication(sys.argv)
    app.setApplicationName("Akeno Downloader")
    app.setApplicationVersion("2.0")
    app.setStyle("Fusion")

    if ICON_PATH and os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    if config.get("theme", "dark") == "dark":
        app.setStyleSheet(DARK_THEME)
    else:
        app.setStyleSheet(LIGHT_THEME)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""
Akeno Downloader v1.2
Entry point for the desktop application.
"""

from gui import YouTubeDownloader


def main() -> None:
    app = YouTubeDownloader()
    app.mainloop()


if __name__ == "__main__":
    main()

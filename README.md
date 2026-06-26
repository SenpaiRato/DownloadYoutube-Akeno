<h1 align="center">🎵 AkenoDownloader</h1>

<p align="center">
  <img width="819" height="745" alt="Akeno Downloader v2.0 Screenshot" src="https://github.com/user-attachments/assets/da19d6ff-d4c4-4ed7-9770-9db11c70fb36" />
</p>

<p align="center">
  <b>Clean, fast, and modern YouTube downloader — built for users who value simplicity, speed, and control.</b>
</p>

<p align="center">
  <a href="https://github.com/SenpaiRato/AkenoDownloader/releases">
    <img src="https://img.shields.io/github/v/release/SenpaiRato/AkenoDownloader?color=6aa6f8&style=for-the-badge" alt="Release">
  </a>
  <a href="https://github.com/SenpaiRato/AkenoDownloader/issues">
    <img src="https://img.shields.io/github/issues/SenpaiRato/AkenoDownloader?color=fcba03&style=for-the-badge" alt="Issues">
  </a>
  <a href="https://github.com/SenpaiRato/AkenoDownloader/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/SenpaiRato/AkenoDownloader?color=00c853&style=for-the-badge" alt="License">
  </a>
  <a href="https://github.com/SenpaiRato/AkenoDownloader/releases">
    <img src="https://img.shields.io/badge/yt--dlp-2026-blueviolet?style=for-the-badge" alt="yt-dlp">
  </a>
</p>

<hr>

<h2>✨ Overview</h2>

<p>
  <b>AkenoDownloader</b> is a lightweight, privacy-respecting YouTube downloader built with <b>PySide6</b> and powered by the latest <b>yt-dlp 2026</b> engine.
  It focuses on speed, simplicity, and full transparency — open source, no telemetry, no ads.
</p>

<hr>

<h2>🚀 Features</h2>

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🎬 <b>High-Res Downloads</b></td>
      <td>Support for 1080p, 2K, 4K and higher (depending on source availability).</td>
    </tr>
    <tr>
      <td>🎧 <b>Audio Extraction</b></td>
      <td>Download videos or extract high-quality audio.</td>
    </tr>
    <tr>
      <td>📁 <b>Custom Save Path</b></td>
      <td>Choose exactly where your videos are saved, directly from the UI.</td>
    </tr>
    <tr>
      <td>🧠 <b>Smart Parsing</b></td>
      <td>Automatically detects available resolutions and formats.</td>
    </tr>
    <tr>
      <td>🔐 <b>Cookie Authentication</b></td>
      <td>Full support for Netscape cookie exports to bypass bot checks.</td>
    </tr>
    <tr>
      <td>🌐 <b>Dynamic Proxy</b></td>
      <td>Auto-detects Windows VPN / system proxy with hotfixed routing.</td>
    </tr>
    <tr>
      <td>⚡ <b>Optimized FFmpeg</b></td>
      <td>Faster downloads and merges with improved FFmpeg integration.</td>
    </tr>
    <tr>
      <td>🎨 <b>Modern PySide6 UI</b></td>
      <td>Lighter, cleaner, and more professional interface.</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🧩 Requirements &amp; Step-by-step Setup</h2>

<blockquote>
  ⚠️ <b>Note:</b> AkenoDownloader does <b>not</b> require the user to install Python or any runtime (unless you run it from source). For the release version, you only need <code>ffmpeg.exe</code> alongside the executable.
</blockquote>

<h3>✳️ Step-by-step Setup</h3>

<ol>
  <li>Export your cookies as <b>Netscape</b> format using a reliable extension like <a href="https://cookie-editor.com">Cookie-Editor</a> (works on all browsers).</li>
  <li>Go into AKENO and Click to the Cookies section, paste it - save.</li>
  <li>you're ready to go! 🎉</li>
</ol>

<blockquote>
  🛑 <b>Important:</b> If the program fails to download, your cookies have likely expired. Re-export them from scratch and replace the contents of <code>cookies.txt</code>.<br>
  ⚠️ <b>Never share your <code>cookies.txt</code> file with anyone — it contains your active login session!</b>
</blockquote>

<hr>

<h2>📂 Release Folder Layout</h2>

<pre><code>AkenoDownloader.exe
ffmpeg.exe
cookies.txt          ← auto-generated
.cookies_ytdlp.txt   ← auto-generated
config.json          ← auto-generated (stores your preferences)
</code></pre>

<hr>

<h2>🧰 Libraries / Dependencies (Only for Source Users)</h2>

<blockquote>
  ℹ️ Users who downloaded the release version do <b>not</b> need to install anything.
</blockquote>

<p>AkenoDownloader v2.0 uses the following Python libraries:</p>

<table>
  <thead>
    <tr>
      <th>Library</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>PySide6</code></td>
      <td>Modern, professional GUI framework</td>
    </tr>
    <tr>
      <td><code>yt_dlp</code> (2026)</td>
      <td>Download and extract videos/audio from YouTube</td>
    </tr>
    <tr>
      <td><code>Pillow</code> (PIL)</td>
      <td>Handle images, logos, and icons</td>
    </tr>
    <tr>
      <td><code>requests</code></td>
      <td>Network requests and proxy handling</td>
    </tr>
    <tr>
      <td><code>json</code></td>
      <td>Parse and write configuration files</td>
    </tr>
    <tr>
      <td><code>threading</code></td>
      <td>Multi-threading for smooth UI performance</td>
    </tr>
    <tr>
      <td><code>os</code> / <code>sys</code></td>
      <td>File system and system operations</td>
    </tr>
    <tr>
      <td><code>re</code></td>
      <td>Regular expressions for text parsing</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🧠 FAQ</h2>

<p><b>❓ Is AkenoDownloader safe to use?</b><br>
✅ Yes. It is fully open source and contains no malware or ads. Some antivirus programs may flag it due to how it accesses videos — these are false positives.</p>

<p><b>❓ Do I need to install Python or any other software?</b><br>
✅ No. The released <code>.exe</code> runs independently. Just make sure <code>ffmpeg.exe</code> and <code>cookies.txt</code> are next to it.</p>

<p><b>❓ Why do I need <code>cookies.txt</code>?</b><br>
✅ Cookies allow the program to bypass YouTube's "Are you a robot?" checks and access higher-quality formats.</p>

<p><b>❓ Which platforms are supported?</b><br>
✅ Windows 10 and later.</p>

<p><b>❓ What video formats can I download?</b><br>
✅ MP4 is supported by default, with resolutions up to 4K/8K when available.</p>

<p><b>❓ My download is slow or failing — what should I do?</b><br>
✅ The dynamic proxy feature is enabled by default and will automatically use your system VPN/proxy. If issues persist, refresh your cookies.</p>

<p><b>❓ How can I contribute or report bugs?</b><br>
✅ You can submit issues on GitHub. (Please note: updates may be slow as this is a personal project.)</p>

<hr>

<p align="center">
  <b>Built with ❤️ by <a href="https://github.com/SenpaiRato">SenpaiRato</a></b>
</p>

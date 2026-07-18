# QIFY Downloader

<p align="center">
  <img src="assets/qify.ico" alt="QIFY Downloader Logo" width="120">
</p>

<p align="center">
  <strong>A modern Windows GUI media downloader built with Python, CustomTkinter, and yt-dlp.</strong>
</p>

##  Quick Start

Install the latest stable version from PyPI:

```bash
pip install qify-downloader
```

Launch the application:

```bash
qify-downloader
```

<p align="center">


![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![GitHub License](https://img.shields.io/github/license/deep-mistry10/QIFY-Downloader)
![GitHub Release](https://img.shields.io/github/v/release/deep-mistry10/QIFY-Downloader)
![GitHub Downloads](https://img.shields.io/github/downloads/deep-mistry10/QIFY-Downloader/total)
[![PyPI Version](https://img.shields.io/pypi/v/qify-downloader)](https://pypi.org/project/qify-downloader/)
![Status](https://img.shields.io/badge/Status-Stable-success)

</p>

---

## Features

-  Download audio as MP3
-  Download videos as MP4
-  Download multiple URLs in a queue
-  Choose your own download folder
-  Real-time progress bar
-  FFmpeg support (bundled with the PyPI package)
-  Modern Windows GUI built with CustomTkinter
-  Live download log
-  Free and open-source software licensed under GPL v3.

---

##  Screenshot

![QIFY Downloader](screenshots/main.png)

---

#  Installation

## Option 1 – Install from PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip install qify-downloader
```

Launch the application:

```bash
qify-downloader
```

Upgrade:

```bash
pip install --upgrade qify-downloader
```

Uninstall:

```bash
pip uninstall qify-downloader
```

**Requirements**

- Windows 10 or Windows 11
- Python 3.10+

> **Note:** FFmpeg is bundled with QIFY Downloader. No separate installation is required.

---

## Option 2 – Download the Windows Executable

1. Open the **Releases** page.

2. Download:

```text
QIFY-Downloader.exe
```

3. Install FFmpeg (required for the standalone executable; see below).

4. Double-click **QIFY-Downloader.exe**.

No Python installation is required.

---

## Option 3 – Run From Source

### Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- FFmpeg

Clone the repository:

```bash
git clone https://github.com/deep-mistry10/QIFY-Downloader.git
```

Go into the folder:

```bash
cd QIFY-Downloader
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

---

#  FFmpeg Installation (Standalone EXE & Source Only)
> **Note:** If you installed QIFY Downloader using `pip install qify-downloader`, FFmpeg is already bundled and you can skip this section.

QIFY Downloader requires **FFmpeg** for audio conversion and video processing.

## Step 1

Official FFmpeg website:

https://ffmpeg.org/download.html

Windows builds (Gyan) direct Download Link:

https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

---

## Step 2

Extract the ZIP file.

---

## Step 3

Install FFmpeg using **one** of these methods.

### Option A (Recommended)

Add FFmpeg's **bin** folder to your Windows **PATH**.

---

### Option B

Copy the **bin** folder to:

```text
C:\ffmpeg\bin
```

Your folder should look like:

```text
C:\
└── ffmpeg
    └── bin
        ├── ffmpeg.exe
        ├── ffprobe.exe
        └── ffplay.exe
```

---

## Step 4

Verify installation.

Open Command Prompt and run:

```bash
ffmpeg -version
```

If version information appears, FFmpeg is installed correctly.

---

#  Python Dependencies

Install using:

```bash
pip install -r requirements.txt
```

Dependencies:

- yt-dlp
- customtkinter

---

#  Project Structure

```
QIFY-Downloader/
│
├── .github/
├── assets/
├── screenshots/
├── main.py
├── README.md
├── LICENSE
├── DISCLAIMER.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── requirements.txt
├── .gitignore
└── .editorconfig
```

---

#  Contributing

Contributions are welcome.

If you'd like to improve QIFY Downloader:

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a Pull Request.

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0 (GPL-3.0).

---

# License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

You are free to:

- Use the software
- Study the source code
- Modify the software
- Redistribute original or modified versions

If you distribute a modified version, you must also distribute the complete corresponding source code under the GPL v3 license.

See the **LICENSE** file for the full license text.

---

# Why GPL v3?

QIFY Downloader is licensed under GPL v3 to ensure that improvements to the software remain open source when distributed.

This helps keep the project free, transparent, and community-driven.

## Credits

QIFY Downloader would not be possible without these excellent open-source projects:

- **yt-dlp** — Media downloading engine
- **FFmpeg** — Audio and video processing
- **CustomTkinter** — Modern desktop user interface

Special thanks to all contributors and maintainers of these projects.

Special thanks to the maintainers and contributors of these projects.

---

## Third-Party Software

QIFY Downloader uses several open-source projects.

For third-party licenses and notices, see **THIRD_PARTY_NOTICES.md**.

# Third-Party Software

QIFY Downloader includes or depends on the following open-source software:

| Software | Purpose | License |
|----------|---------|---------|
| yt-dlp | Media downloading engine | Unlicense |
| FFmpeg | Audio/video processing | LGPL v2.1+ or GPL v2+ (depending on the bundled build) |
| CustomTkinter | Modern GUI framework | MIT License |


### FFmpeg

The PyPI package of QIFY Downloader includes a bundled FFmpeg build for user convenience.

If you are using the standalone executable or running the project from source, you may need to install FFmpeg separately unless otherwise stated.

FFmpeg is developed by the FFmpeg project and is licensed under its own license.

https://ffmpeg.org/

The bundled FFmpeg binaries remain the property of the FFmpeg project and are distributed under the FFmpeg license. QIFY Downloader does not modify or claim ownership of FFmpeg.

### yt-dlp

QIFY Downloader uses yt-dlp for downloading media from supported websites.

https://github.com/yt-dlp/yt-dlp

### CustomTkinter

The graphical user interface is built using CustomTkinter.

https://github.com/TomSchimansky/CustomTkinter

#  Disclaimer

QIFY Downloader is an independent open-source application.

It is **not affiliated with or endorsed by YouTube, Google, or any other content provider**.

Users are solely responsible for ensuring that their use of this software complies with applicable copyright laws and the terms of service of the websites they access.

The developers do not encourage or endorse copyright infringement.

---

#  Support

If you find this project useful, please consider giving it a ⭐ on GitHub.

It helps others discover the project and supports future development.

---

# Windows Security Notice

QIFY Downloader is an open-source application.

Because the Windows executable is not digitally signed, Windows SmartScreen or Microsoft Defender may display a warning the first time you run it.

You can:

- Inspect the source code on GitHub.
- Build the application yourself from source.
- Verify releases before running them.

---

© 2026 Deep Mistry

Made with ❤️ by **Deep Mistry**

# QIFY Downloader

<p align="center">
  <img src="assets/qify.ico" alt="QIFY Downloader Logo" width="120">
</p>

<p align="center">
  <strong>A modern Windows GUI media downloader built with Python, CustomTkinter, and yt-dlp.</strong>
</p>

<p align="center">

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-success)

</p>

---

## Features

-  Download audio in MP3 format
-  Download videos in MP4 format
-  Download multiple URLs in a queue
-  Choose your own download folder
-  Real-time progress bar
-  Automatic FFmpeg detection
-  Modern Windows GUI built with CustomTkinter
-  Live download log
-  Free and open source

---

##  Screenshot

![QIFY Downloader](screenshots/main.png)

---

#  Installation

## Option 1 – Download the Windows Executable (Recommended)

1. Open the **Releases** page.

2. Download the latest:

```
QIFY-Downloader.exe
```

3. Install FFmpeg (see below).

4. Double-click **QIFY-Downloader.exe**.

No Python installation is required.

---

## Option 2 – Run From Source

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

#  FFmpeg Installation

QIFY Downloader requires **FFmpeg** for audio conversion and video processing.

## Step 1

Download FFmpeg from the official website:

https://ffmpeg.org/download.html

Choose a **Windows build**.
or **Direct Download Link**

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

---

#  License

This project is licensed under the **MIT License**.

See the **LICENSE** file for details.

---

#  Credits

QIFY Downloader uses the excellent **yt-dlp** project for media extraction and downloading.

Special thanks to the **yt-dlp** contributors for maintaining such an amazing open-source project.

---

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
Windows Security Notice

QIFY Downloader is an open-source application. Because the Windows executable is not digitally signed, Windows Smart App Control or Microsoft Defender may display a warning the first time you run it. You can inspect the source code on GitHub or build the application yourself from source if you prefer.

Made with ❤️ by **Deep Mistry**

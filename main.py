# QIFY Downloader
# Copyright (C) 2026 Deep Mistry
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

import yt_dlp
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
import threading
import re
import sys
import subprocess
import shutil
import ctypes

from __version__ import __version__
cancel_download = False


def cancel_download_func():
    global cancel_download
    cancel_download = True
    status_var.set("Cancelling...")


# ---------------- UI THEME ----------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ---------------- Windows Configuration ----------------
HOME = str(Path.home())
DOWNLOAD_FOLDER = os.path.join(HOME, "Desktop", "YT_Downloads")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------------- FFmpeg Detection ----------------

from importlib.resources import files, as_file

def get_ffmpeg_path():
    """
    Search order:
    1. Bundled FFmpeg (PyPI)
    2. Bundled FFmpeg (PyInstaller)
    3. FFmpeg in PATH
    4. C:\ffmpeg\bin
    """

    # Running from PyInstaller EXE
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "ffmpeg"

    # Running from PyPI / source
    else:
        bundled = Path(files("qify_downloader").joinpath("ffmpeg"))

    # Bundled FFmpeg
    if (bundled / "ffmpeg.exe").exists():
        return bundled

    # FFmpeg in PATH
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return Path(ffmpeg).parent

    # Legacy install
    legacy = Path(r"C:\ffmpeg\bin")
    if (legacy / "ffmpeg.exe").exists():
        return legacy

    return None


FFMPEG_PATH = get_ffmpeg_path()

if FFMPEG_PATH:
    os.environ["PATH"] = str(FFMPEG_PATH) + os.pathsep + os.environ["PATH"]


def get_video_format():
    quality = video_quality.get()

    quality_map = {
        "2160p (4K)": 2160,
        "1440p": 1440,
        "1080p": 1080,
        "720p": 720,
        "480p": 480,
        "360p": 360,
    }

    if quality == "Best Available":
        return "bestvideo+bestaudio/best"

    height = quality_map.get(quality, 1080)

    return (
        f"bestvideo[height<={height}]"
        f"+bestaudio/best[height<={height}]"
    )


# ---------------- FUNCTIONS ----------------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)


def validate_ffmpeg():
    if FFMPEG_PATH and (Path(FFMPEG_PATH) / "ffmpeg.exe").exists():
        return True

    messagebox.showerror(
        "FFmpeg Not Found",
        "FFmpeg could not be found.\n\n"
        "Please reinstall QIFY Downloader or install FFmpeg."
    )
    return False


def add_urls():
    urls = url_entry.get("1.0", "end").strip().splitlines()
    for u in urls:
        if u.strip() and u not in url_list.get(0, "end"):
            url_list.insert("end", u)
    url_entry.delete("1.0", "end")


def remove_selected():
    selected = url_list.curselection()
    for i in reversed(selected):
        url_list.delete(i)


def clear_urls():
    url_list.delete(0, "end")


def progress_hook(d):
    global cancel_download

    if cancel_download:
        raise Exception("Download cancelled by user")

    if d['status'] == 'downloading':
        try:
            percent = float(d.get('_percent_str', '0.0%').replace('%', '')) / 100
            pb.set(percent)
            status_var.set(
                f"{d.get('_percent_str','')} | "
                f"{d.get('_speed_str','')} | "
                f"ETA {d.get('_eta_str','')}"
            )
        except:
            pass

    elif d['status'] == 'finished':
        log_text.insert("end", f"\nFinished: {d['filename']}\n")
        log_text.see("end")


def disable_ui():
    for btn in [start_btn, add_btn, remove_btn, clear_btn, browse_btn, audio_radio, video_radio]:
        btn.configure(state="disabled")
    url_entry.configure(state="disabled")
    folder_entry.configure(state="disabled")


def enable_ui():
    for btn in [start_btn, add_btn, remove_btn, clear_btn, browse_btn, audio_radio, video_radio]:
        btn.configure(state="normal")

    url_entry.configure(state="normal")
    folder_entry.configure(state="normal")

    cancel_btn.configure(state="disabled")


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert("end", string)
        self.text_widget.see("end")

    def flush(self):
        pass


def start_download():
    global cancel_download
    cancel_download = False

    if not validate_ffmpeg():
        return

    urls = url_list.get(0, "end")
    if not urls:
        messagebox.showerror("Error", "No URLs added!")
        return

    folder = Path(folder_var.get())
    audio_folder = folder / "Audios"
    video_folder = folder / "Videos"
    audio_folder.mkdir(parents=True, exist_ok=True)
    video_folder.mkdir(parents=True, exist_ok=True)

    base_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'progress_hooks': [progress_hook],
        'quiet': False,
        'ignoreerrors': True,
        'retries': 10,
        'socket_timeout': 30,
        'http_headers': {
            "User-Agent": "Mozilla/5.0",
        },

        'sleep_interval': 2,
        'max_sleep_interval': 5,
    }

    if download_choice.get() == "audio":
        ydl_opts = {
            **base_opts,
            'outtmpl': os.path.join(audio_folder, "%(title)s.%(ext)s"),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'writethumbnail': True,
            'addmetadata': True,
        }
    else:
        ydl_opts = {
            **base_opts,
            'format': get_video_format(),
            'outtmpl': os.path.join(video_folder, "%(title)s.%(ext)s"),
            'merge_output_format': 'mp4',
        }

    def run_download():
        pb.set(0)
        status_var.set("Downloading...")
        disable_ui()
        cancel_btn.configure(state="normal")

        for i, url in enumerate(urls, 1):
            try:
                print(f"\n[{i}/{len(urls)}] Downloading: {url}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print("Done\n")
            except Exception as e:
                if cancel_download:
                    print("Download cancelled by user.")
                    break
                else:
                    print("Error:", e)

        pb.set(0)
        enable_ui()
        cancel_btn.configure(state="disabled")

        if cancel_download:
            status_var.set("Download Cancelled")
            messagebox.showinfo("Cancelled", "Download cancelled.")
        else:
            status_var.set("All downloads finished!")
            messagebox.showinfo("Done", "All downloads completed!")

    threading.Thread(
        target=run_download,
        daemon=True
    ).start()


# ---------------- UI ----------------

root = ctk.CTk()

# Windows App ID
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "com.qify.downloader"
)

try:
    if getattr(sys, "frozen", False):
        icon_path = os.path.join(sys._MEIPASS, "assets", "qify.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "qify.ico")

    root.iconbitmap(icon_path)

except Exception as e:
    print("Could not load icon:", e)

root.title(f"QIFY Downloader v{__version__} - Windows")
root.geometry("900x650")

url_frame = ctk.CTkFrame(root)
url_frame.pack(fill="x", padx=10, pady=5)
ctk.CTkLabel(url_frame, text="Video URLs (one per line):").pack(anchor="w", padx=5)

url_entry = ctk.CTkTextbox(url_frame, height=80)
url_entry.pack(fill="x", padx=5, pady=5)

list_frame = ctk.CTkFrame(root)
list_frame.pack(fill="both", expand=True, padx=10, pady=5)

url_list = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, bg="#2B2B2B", fg="white")
url_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)

scroll = tk.Scrollbar(list_frame, orient="vertical", command=url_list.yview)
scroll.pack(side="left", fill="y")
url_list.config(yscrollcommand=scroll.set)

btn_frame = ctk.CTkFrame(list_frame, width=140)
btn_frame.pack(side="left", fill="y", padx=5)

add_btn = ctk.CTkButton(btn_frame, text="Add URLs", command=add_urls)
add_btn.pack(fill="x", pady=5)

remove_btn = ctk.CTkButton(btn_frame, text="Remove Selected", command=remove_selected)
remove_btn.pack(fill="x", pady=5)

clear_btn = ctk.CTkButton(btn_frame, text="Clear List", command=clear_urls)
clear_btn.pack(fill="x", pady=5)

folder_frame = ctk.CTkFrame(root)
folder_frame.pack(fill="x", padx=10, pady=5)

folder_var = ctk.StringVar(value=DOWNLOAD_FOLDER)
folder_entry = ctk.CTkEntry(folder_frame, textvariable=folder_var, width=650)
folder_entry.pack(side="left", padx=5)

browse_btn = ctk.CTkButton(folder_frame, text="Browse", command=browse_folder)
browse_btn.pack(side="left", padx=5)

choice_frame = ctk.CTkFrame(root)
choice_frame.pack(fill="x", padx=10, pady=5)

download_choice = ctk.StringVar(value="audio")

audio_radio = ctk.CTkRadioButton(
    choice_frame,
    text="Audio (MP3)",
    variable=download_choice,
    value="audio",
    command=lambda: quality_menu.configure(state="disabled")
)
audio_radio.pack(side="left", padx=10)

video_radio = ctk.CTkRadioButton(
    choice_frame,
    text="Video (MP4)",
    variable=download_choice,
    value="video",
    command=lambda: quality_menu.configure(state="normal")
)
video_radio.pack(side="left", padx=10)

# Video quality selector
video_quality = ctk.StringVar(value="Best Available")

quality_label = ctk.CTkLabel(
    choice_frame,
    text="Video Quality:"
)
quality_label.pack(side="left", padx=(30, 5))

quality_menu = ctk.CTkOptionMenu(
    choice_frame,
    variable=video_quality,
    values=[
        "Best Available",
        "2160p (4K)",
        "1440p",
        "1080p",
        "720p",
        "480p",
        "360p"
    ],
    state="disabled"
)
quality_menu.pack(side="left", padx=5)

start_btn = ctk.CTkButton(root, text="Start Download", command=start_download)
cancel_btn = ctk.CTkButton(
    root,
    text="Cancel Download",
    command=cancel_download_func,
    state="disabled"
)
start_btn.pack(pady=10)
cancel_btn.pack(pady=5)

pb = ctk.CTkProgressBar(root, width=750)
pb.pack(pady=5)

status_var = ctk.StringVar(value="Idle")
ctk.CTkLabel(root, textvariable=status_var).pack()

log_frame = ctk.CTkFrame(root)
log_frame.pack(fill="both", expand=True, padx=10, pady=5)

log_text = ctk.CTkTextbox(log_frame)
log_text.pack(fill="both", expand=True)

version_frame = ctk.CTkFrame(root, fg_color="transparent")
version_frame.pack(fill="x", padx=10, pady=(0, 5))

version_label = ctk.CTkLabel(
    version_frame,
    text=f"QIFY Downloader v{__version__}",
    text_color="gray"
)
version_label.pack(side="right")

sys.stdout = StdoutRedirector(log_text)
sys.stderr = StdoutRedirector(log_text)

def main():
    root.mainloop()


if __name__ == "__main__":
    main()
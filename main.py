
# ============================================================
# QIFY Downloader
# Copyright (C) 2026 Deep Mistry
#
# Licensed under the GNU General Public License v3.0 or later.
# ============================================================

import os
import sys
import re
import shutil
import threading
import queue
import ctypes
import tkinter as tk
import time

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import yt_dlp

from yt_dlp.utils import DownloadCancelled
from __version__ import __version__


# ============================================================
# CONFIGURATION
# ============================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_ID = "com.qify.downloader"

DOWNLOAD_FOLDER = Path.home() / "Desktop" / "YT_Downloads"

DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

cancel_event = threading.Event()
event_queue = queue.Queue()

download_thread = None
closing = False


# ============================================================
# FFMPEG DETECTION
# ============================================================

def get_ffmpeg_path():
    candidates = []

    if getattr(sys, "frozen", False):
        candidates.extend([
            Path(sys._MEIPASS) / "ffmpeg",
            Path(sys.executable).parent / "ffmpeg",
        ])
    else:
        candidates.append(Path(__file__).resolve().parent / "ffmpeg")

    candidates.append(Path(r"C:\ffmpeg\bin"))

    for folder in candidates:
        if (folder / "ffmpeg.exe").is_file():
            return folder

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        return Path(ffmpeg).resolve().parent

    return None


FFMPEG_PATH = get_ffmpeg_path()


def validate_ffmpeg():
    if FFMPEG_PATH and (FFMPEG_PATH / "ffmpeg.exe").is_file():
        return True

    messagebox.showerror(
        "FFmpeg Not Found",
        "FFmpeg could not be found.\n\n"
        "Please reinstall QIFY Downloader or install FFmpeg."
    )

    return False


# ============================================================
# VIDEO FORMAT
# ============================================================

def get_video_format(quality):

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
        f"bestvideo[height<={height}][ext=mp4]"
        f"+bestaudio[ext=m4a]/"
        f"best[height<={height}][ext=mp4]/"
        f"bestvideo[height<={height}]+bestaudio/"
        f"best[height<={height}]"
    )


# ============================================================
# LOGGING
# ============================================================

def log(message):
    event_queue.put(("log", str(message)))


class YDLLogger:

    ANSI_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

    def clean(self, message):
        return self.ANSI_PATTERN.sub("", str(message)).strip()

    def debug(self, message):
        # Progress is handled separately by progress_hook.
        # Prevent terminal output from filling the GUI log.
        pass

    def warning(self, message):
        log("Warning: " + self.clean(message))

    def error(self, message):
        log("Error: " + self.clean(message))


# ============================================================
# PROGRESS FORMATTING
# ============================================================

def format_bytes(size):

    if size is None:
        return "Unknown"

    size = float(size)

    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):

        if size < 1024 or unit == "TiB":
            return f"{size:.2f} {unit}"

        size /= 1024

    return "Unknown"


def format_time(seconds):

    if seconds is None:
        return "Calculating..."

    seconds = max(0, int(seconds))

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


# ============================================================
# PROGRESS HOOK
# ============================================================

last_progress_update = 0


def progress_hook(data):

    global last_progress_update

    if cancel_event.is_set():
        raise DownloadCancelled("Download cancelled by user")

    status = data.get("status")

    if status == "downloading":

        # Limit GUI updates to approximately 4 per second.
        now = time.monotonic()

        if now - last_progress_update < 0.25:
            return

        last_progress_update = now

        downloaded = data.get("downloaded_bytes", 0)

        total = (
            data.get("total_bytes")
            or data.get("total_bytes_estimate")
        )

        speed = data.get("speed")
        eta = data.get("eta")

        if total and total > 0:

            percent = min(1.0, downloaded / total)

            percent_text = f"{percent * 100:.1f}%"

            size_text = (
                f"{format_bytes(downloaded)} / "
                f"{format_bytes(total)}"
            )

        else:

            percent = 0

            percent_text = "Calculating..."

            size_text = format_bytes(downloaded)

        speed_text = (
            f"{format_bytes(speed)}/s"
            if speed else "Calculating..."
        )

        eta_text = format_time(eta)

        info = data.get("info_dict") or {}

        filename = (
            info.get("title")
            or Path(data.get("filename", "Video")).name
        )

        status_text = (
            f"{filename} | {percent_text} | "
            f"{size_text} | {speed_text} | "
            f"ETA: {eta_text}"
        )

        event_queue.put((
            "progress",
            percent,
            status_text,
        ))

    elif status == "finished":

        filename = data.get("filename", "Downloaded file")

        event_queue.put((
            "progress",
            1.0,
            "Download finished. Processing file..."
        ))

        log(f"Download stream finished: {Path(filename).name}")


# ============================================================
# DOWNLOAD OPTIONS
# ============================================================

def get_download_options(folder, mode, quality):

    is_audio = mode == "audio"

    output_folder = folder / (
        "Audios" if is_audio else "Videos"
    )

    output_folder.mkdir(parents=True, exist_ok=True)

    options = {
        "outtmpl": str(
            output_folder / "%(title).200B.%(ext)s"
        ),

        "ffmpeg_location": str(FFMPEG_PATH),

        "windowsfilenames": True,

        "progress_hooks": [progress_hook],

        "logger": YDLLogger(),

        "quiet": True,
        "noprogress": True,
        "no_warnings": False,
        "ignoreerrors": False,

        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 30,

        "sleep_interval": 2,
        "max_sleep_interval": 5,

        "http_headers": {
            "User-Agent": "Mozilla/5.0",
        },
    }

    if is_audio:

        options.update({
            "format": "bestaudio/best",

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {
                    "key": "EmbedThumbnail",
                },
                {
                    "key": "FFmpegMetadata",
                },
            ],

            "writethumbnail": True,
            "addmetadata": True,
        })

    else:

        options.update({
            "format": get_video_format(quality),
            "merge_output_format": "mp4",
        })

    return options


# ============================================================
# URL MANAGEMENT
# ============================================================

def add_urls():

    urls = url_entry.get("1.0", "end").splitlines()

    existing = set(url_list.get(0, "end"))

    for url in urls:

        url = url.strip()

        if url and url not in existing:
            url_list.insert("end", url)
            existing.add(url)

    url_entry.delete("1.0", "end")


def remove_selected():

    for index in reversed(url_list.curselection()):
        url_list.delete(index)


def clear_urls():
    url_list.delete(0, "end")


def browse_folder():

    folder = filedialog.askdirectory()

    if folder:
        folder_var.set(folder)


# ============================================================
# UI STATE
# ============================================================

def set_ui_state(enabled):

    state = "normal" if enabled else "disabled"

    widgets = [
        start_btn,
        add_btn,
        remove_btn,
        clear_btn,
        browse_btn,
        audio_radio,
        video_radio,
        quality_menu,
    ]

    for widget in widgets:
        widget.configure(state=state)

    url_entry.configure(state=state)
    folder_entry.configure(state=state)

    if enabled and download_choice.get() == "audio":
        quality_menu.configure(state="disabled")


def update_quality():

    quality_menu.configure(
        state=(
            "normal"
            if download_choice.get() == "video"
            else "disabled"
        )
    )


# ============================================================
# CANCELLATION
# ============================================================

def cancel_download():

    if download_thread and download_thread.is_alive():

        cancel_event.set()

        cancel_btn.configure(state="disabled")

        status_var.set("Cancelling...")


# ============================================================
# DOWNLOAD ENGINE
# ============================================================

def run_download(urls, options):

    successful = 0
    failed = 0
    cancelled = False

    try:

        for index, url in enumerate(urls, 1):

            if cancel_event.is_set():
                cancelled = True
                break

            log(f"\n[{index}/{len(urls)}] Downloading: {url}")

            try:

                with yt_dlp.YoutubeDL(options) as downloader:
                    result = downloader.download([url])

                if result == 0:
                    successful += 1
                    log(f"Successfully completed: {url}")

                else:
                    if cancel_event.is_set():
                        cancelled = True
                        break

                    failed += 1
                    log(f"Download failed: {url}")

            except DownloadCancelled:

                cancelled = True
                log("Download cancelled by user.")
                break

            except Exception as error:

                if cancel_event.is_set():
                    cancelled = True
                    log("Download cancelled by user.")
                    break

                failed += 1
                log(f"Download error: {error}")

        cancelled = cancelled or cancel_event.is_set()

    except Exception as error:

        failed += 1
        log(f"Application error: {error}")

    finally:

        event_queue.put((
            "done",
            successful,
            failed,
            cancelled,
        ))


# ============================================================
# START DOWNLOAD
# ============================================================

def start_download():

    global download_thread

    if download_thread and download_thread.is_alive():
        return

    urls = [
        url.strip()
        for url in url_list.get(0, "end")
        if url.strip()
    ]

    if not urls:

        messagebox.showerror(
            "Error",
            "Please add at least one URL."
        )

        return

    folder = Path(folder_var.get()).expanduser()

    try:

        folder.mkdir(parents=True, exist_ok=True)

        if not folder.is_dir():
            raise NotADirectoryError(str(folder))

    except OSError as error:

        messagebox.showerror(
            "Folder Error",
            str(error)
        )

        return

    if not validate_ffmpeg():
        return

    # Capture GUI values on the main thread.

    mode = download_choice.get()
    quality = video_quality.get()

    try:

        options = get_download_options(
            folder,
            mode,
            quality,
        )

    except (OSError, ValueError) as error:

        messagebox.showerror(
            "Configuration Error",
            str(error)
        )

        return

    cancel_event.clear()

    set_ui_state(False)

    cancel_btn.configure(state="normal")

    pb.set(0)
    status_var.set("Preparing downloads...")

    download_thread = threading.Thread(
        target=run_download,
        args=(urls, options),
        daemon=True,
        name="QIFY-Download-Worker",
    )

    download_thread.start()


# ============================================================
# GUI EVENT PROCESSOR
# ============================================================

def process_events():

    try:

        while True:

            event = event_queue.get_nowait()

            event_type = event[0]

            if event_type == "log":

                log_text.insert(
                    "end",
                    event[1] + "\n"
                )

                log_text.see("end")

            elif event_type == "progress":

                _, percent, status = event

                pb.set(percent)
                status_var.set(status)

            elif event_type == "done":

                global download_thread

                _, successful, failed, cancelled = event

                download_thread = None

                set_ui_state(True)

                cancel_btn.configure(state="disabled")

                pb.set(0)

                if closing:
                    continue

                if cancelled:

                    status_var.set("Download Cancelled")

                    messagebox.showinfo(
                        "Cancelled",
                        f"Successful: {successful}\n"
                        f"Failed: {failed}\n\n"
                        "Download cancelled."
                    )

                else:

                    status_var.set("All downloads finished!")

                    messagebox.showinfo(
                        "Download Complete",
                        f"Successful: {successful}\n"
                        f"Failed: {failed}"
                    )

    except queue.Empty:
        pass

    if root.winfo_exists():
        root.after(100, process_events)


# ============================================================
# APPLICATION SHUTDOWN
# ============================================================

def finish_close():

    if download_thread and download_thread.is_alive():

        root.after(100, finish_close)

    else:

        root.destroy()


def on_close():

    global closing

    if closing:
        return

    if download_thread and download_thread.is_alive():

        confirm = messagebox.askyesno(
            "Exit QIFY Downloader",
            "A download is currently running.\n\n"
            "Cancel the download and exit?"
        )

        if not confirm:
            return

        closing = True

        cancel_event.set()

        set_ui_state(False)

        cancel_btn.configure(state="disabled")

        status_var.set("Cancelling before exit...")

        finish_close()

    else:

        root.destroy()


# ============================================================
# GUI INITIALIZATION
# ============================================================

root = ctk.CTk()

# Windows App ID

if os.name == "nt":

    try:

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_ID
        )

    except (AttributeError, OSError):
        pass


# Application icon

try:

    if getattr(sys, "frozen", False):

        icon_path = (
            Path(sys._MEIPASS)
            / "assets"
            / "qify.ico"
        )

    else:

        icon_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "qify.ico"
        )

    root.iconbitmap(str(icon_path))

except (OSError, tk.TclError):
    pass


root.title(
    f"QIFY Downloader v{__version__} - Windows"
)

root.geometry("900x650")
root.minsize(700, 550)


# ============================================================
# URL INPUT
# ============================================================

url_frame = ctk.CTkFrame(root)
url_frame.pack(fill="x", padx=10, pady=5)

ctk.CTkLabel(
    url_frame,
    text="Video URLs (one per line):"
).pack(anchor="w", padx=5)

url_entry = ctk.CTkTextbox(
    url_frame,
    height=80,
)

url_entry.pack(
    fill="x",
    padx=5,
    pady=5,
)


# ============================================================
# URL LIST
# ============================================================

list_frame = ctk.CTkFrame(root)

list_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5,
)

url_list = tk.Listbox(
    list_frame,
    selectmode=tk.MULTIPLE,
    bg="#2B2B2B",
    fg="white",
    selectbackground="#1F6AA5",
)

url_list.pack(
    side="left",
    fill="both",
    expand=True,
    padx=5,
    pady=5,
)

scroll = tk.Scrollbar(
    list_frame,
    orient="vertical",
    command=url_list.yview,
)

scroll.pack(side="left", fill="y")

url_list.configure(
    yscrollcommand=scroll.set
)


# ============================================================
# URL BUTTONS
# ============================================================

btn_frame = ctk.CTkFrame(
    list_frame,
    width=140,
)

btn_frame.pack(
    side="left",
    fill="y",
    padx=5,
)

add_btn = ctk.CTkButton(
    btn_frame,
    text="Add URLs",
    command=add_urls,
)

add_btn.pack(fill="x", pady=5)

remove_btn = ctk.CTkButton(
    btn_frame,
    text="Remove Selected",
    command=remove_selected,
)

remove_btn.pack(fill="x", pady=5)

clear_btn = ctk.CTkButton(
    btn_frame,
    text="Clear List",
    command=clear_urls,
)

clear_btn.pack(fill="x", pady=5)


# ============================================================
# DOWNLOAD FOLDER
# ============================================================

folder_frame = ctk.CTkFrame(root)

folder_frame.pack(
    fill="x",
    padx=10,
    pady=5,
)

folder_var = ctk.StringVar(
    value=str(DOWNLOAD_FOLDER)
)

folder_entry = ctk.CTkEntry(
    folder_frame,
    textvariable=folder_var,
    width=650,
)

folder_entry.pack(
    side="left",
    padx=5,
)

browse_btn = ctk.CTkButton(
    folder_frame,
    text="Browse",
    command=browse_folder,
)

browse_btn.pack(
    side="left",
    padx=5,
)


# ============================================================
# DOWNLOAD TYPE AND QUALITY
# ============================================================

choice_frame = ctk.CTkFrame(root)

choice_frame.pack(
    fill="x",
    padx=10,
    pady=5,
)

download_choice = ctk.StringVar(
    value="audio"
)

video_quality = ctk.StringVar(
    value="Best Available"
)

audio_radio = ctk.CTkRadioButton(
    choice_frame,
    text="Audio (MP3)",
    variable=download_choice,
    value="audio",
    command=update_quality,
)

audio_radio.pack(
    side="left",
    padx=10,
)

video_radio = ctk.CTkRadioButton(
    choice_frame,
    text="Video (MP4)",
    variable=download_choice,
    value="video",
    command=update_quality,
)

video_radio.pack(
    side="left",
    padx=10,
)

quality_label = ctk.CTkLabel(
    choice_frame,
    text="Video Quality:",
)

quality_label.pack(
    side="left",
    padx=(30, 5),
)

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
        "360p",
    ],
    state="disabled",
)

quality_menu.pack(
    side="left",
    padx=5,
)


# ============================================================
# DOWNLOAD BUTTONS
# ============================================================

start_btn = ctk.CTkButton(
    root,
    text="Start Download",
    command=start_download,
)

start_btn.pack(pady=10)

cancel_btn = ctk.CTkButton(
    root,
    text="Cancel Download",
    command=cancel_download,
    state="disabled",
)

cancel_btn.pack(pady=5)


# ============================================================
# PROGRESS
# ============================================================

pb = ctk.CTkProgressBar(
    root,
    width=750,
)

pb.pack(pady=5)
pb.set(0)

status_var = ctk.StringVar(
    value="Idle"
)

ctk.CTkLabel(
    root,
    textvariable=status_var,
).pack()


# ============================================================
# LOG WINDOW
# ============================================================

log_frame = ctk.CTkFrame(root)

log_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5,
)

log_text = ctk.CTkTextbox(log_frame)

log_text.pack(
    fill="both",
    expand=True,
)


# ============================================================
# VERSION
# ============================================================

version_frame = ctk.CTkFrame(
    root,
    fg_color="transparent",
)

version_frame.pack(
    fill="x",
    padx=10,
    pady=(0, 5),
)

version_label = ctk.CTkLabel(
    version_frame,
    text=f"QIFY Downloader v{__version__}",
    text_color="gray",
)

version_label.pack(side="right")


# ============================================================
# START APPLICATION
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    on_close,
)


def main():
    root.after(100, process_events)
    root.mainloop()


if __name__ == "__main__":
    main()

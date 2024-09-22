import re
import threading
import logging
import customtkinter as ctk
from pytubefix import Playlist, YouTube, exceptions
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from CTkMessagebox import CTkMessagebox
import os
# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '-', filename)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(exceptions.VideoUnavailable))
def download_video(video_url, resolution, output_path=None, is_single_video=False):
    try:
        yt = YouTube(video_url, on_progress_callback=progress_function)
        video_streams = yt.streams.filter(res=resolution)

        video_filename = sanitize_filename(f"{yt.title}.mp4")
        video_path = os.path.join(output_path if output_path else os.getcwd(), video_filename)

        if os.path.exists(video_path):
            CTkMessagebox(title="Info", message=f"{video_filename} already exists")
            return

        if not video_streams:
            CTkMessagebox(title="Info", message=f"No streams available for {resolution}. Downloading highest resolution available.")
            highest_resolution_stream = yt.streams.get_highest_resolution()
            download_with_retries(highest_resolution_stream, video_path)
        else:
            video_stream = video_streams.first()
            download_with_retries(video_stream, "video.mp4")

            audio_stream = yt.streams.get_audio_only()
            download_with_retries(audio_stream, "audio.mp4")

            os.system(
                "ffmpeg -y -i video.mp4 -i audio.mp4 -c:v copy -c:a aac final.mp4 -loglevel quiet -stats")
            os.rename("final.mp4", video_path)
            os.remove("video.mp4")
            os.remove("audio.mp4")

        if is_single_video:
            CTkMessagebox(title="Success", message=f"Downloaded {video_filename} successfully!")
    except exceptions.VideoUnavailable as e:
        logging.error(f"Error downloading video: {e}")
        CTkMessagebox(title="Error", message=f"Error downloading video: {e}")
        raise

def download_playlist(playlist_url, resolution):
    playlist = Playlist(playlist_url)
    playlist_name = sanitize_filename(re.sub(r'\W+', '-', playlist.title))

    if not os.path.exists(playlist_name):
        os.mkdir(playlist_name)

    errors = []
    for index, video in enumerate(tqdm(playlist.videos, desc="Downloading playlist", unit="video"), start=1):
        try:
            download_video(video.watch_url, resolution, output_path=playlist_name)
        except exceptions.VideoUnavailable as e:
            error_message = f"Error downloading video {index}: {e}"
            logging.error(error_message)
            errors.append(error_message)
        except Exception as e:
            error_message = f"Unexpected error downloading video {index}: {e}"
            logging.error(error_message)
            errors.append(error_message)

    if errors:
        CTkMessagebox(title="Errors", message="\n".join(errors))
    else:
        CTkMessagebox(title="Success", message=f"All videos in the playlist '{playlist.title}' have been downloaded successfully!")

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_with_retries(stream, filename):
    stream.download(filename=filename)

def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Downloading... {percentage_of_completion:.2f}% complete", end="\r")

def start_download():
    url = url_entry.get().strip()
    resolution = resolution_var.get()

    if not url:
        CTkMessagebox(title="Error", message="Please enter a URL.")
        return

    def download_task():
        try:
            playlist = Playlist(url)
            if playlist.videos:
                download_playlist(url, resolution)
            else:
                download_video(url, resolution, is_single_video=True)
        except KeyError:
            download_video(url, resolution, is_single_video=True)
        except Exception as e:
            logging.error(f"Error in download task: {e}")
            CTkMessagebox(title="Error", message=str(e))

    threading.Thread(target=download_task).start()

# GUI setup
ctk.set_appearance_mode("System")  # Use system theme
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("YouTube Downloader")

frame = ctk.CTkFrame(root)
frame.grid(row=0, column=0, padx=5, pady=5, sticky=(ctk.W, ctk.E, ctk.N, ctk.S))

url_label = ctk.CTkLabel(frame, text="Enter the URL:")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky=ctk.W)

url_entry = ctk.CTkEntry(frame, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(ctk.W, ctk.E))

resolution_label = ctk.CTkLabel(frame, text="Select resolution:")
resolution_label.grid(row=1, column=0, padx=5, pady=5, sticky=ctk.W)

resolutions = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
resolution_var = ctk.StringVar(value=resolutions[0])
resolution_dropdown = ctk.CTkComboBox(frame, variable=resolution_var, values=resolutions)
resolution_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=(ctk.W, ctk.E))

download_button = ctk.CTkButton(frame, text="Download", command=start_download)
download_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()

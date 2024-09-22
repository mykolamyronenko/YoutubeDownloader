# FFmpeg Video Merger

Youtube Downloader is a Python GUI wrapper for pytubefix, that allows you to downnload videos from YouTube.

## Features

- Select multiple video files to merge.
- Specify the input and output file locations.
- Progress bar to show the merging process.

## Requirements
- Python 3.7+
- FFmpeg installed and accessible in the system's PATH.
- The following Python libraries:
  - `customtkinter`
  - `CTkMessagebox`
  - `pytubefix`
  - `tenacity`
  - `tqdm`

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/mykolamyronenko/YoutubeDownloader.git
   cd YoutubeDownloader
   ```

2. **Create a virtual environment:**
   ```
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
      ```
      .venv\Scripts\activate
      ```

   - On macOS/Linux:
      ```
      source .venv/bin/activate
      ```
   
4. **Activate the virtual environment:**
    ```  
    pip install -r requirements.txt
    ```

4. Ensure FFmpeg and FFprobe are installed and accessible in your system's PATH:
   ```
   ffmpeg -version
   ```

## Usage

1. Run the application:
    ```
    python main.py
    ```

2. Use the GUI to insert link to video or playlist specify the output resolution, and start the downloading process.




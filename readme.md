# YouTube Video Downloader

This project is a simple YouTube video downloader built with Python. It allows users to download videos from YouTube by providing the video URL.

## Features

- Download videos from YouTube
- Choose video resolution
- Streams list shows one high-quality option per resolution
- Video is merged with the best available audio using FFmpeg
- Prefers the video's original audio track when multiple languages are available
- Simple and easy to use

## Requirements

- Python 3.x
- `yt-dlp` library

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/henrique-trevisan/Youtube-video-downloader.git
    ```
2. Navigate to the project directory:
    ```bash
    cd youtube-video-downloader
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

On Windows, FFmpeg is bundled with this repository under `thirdParty/ffmpeg/bin`.
The application automatically uses it if no system FFmpeg is found.

## Usage

1. Run the script:
    ```sh
    python main.py
    ```
2. Enter the URL of the YouTube video you want to download.
3. Choose the desired resolution.
4. The video will be downloaded to the current directory.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

For any questions or suggestions, please contact trehen30@gmail.com.

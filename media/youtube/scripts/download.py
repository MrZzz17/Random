"""
Download YouTube videos or playlists using yt-dlp.
Usage:
  python download.py --url "https://youtube.com/watch?v=..."
  python download.py --url "https://youtube.com/playlist?list=..." --audio-only
"""

import argparse
import os
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../downloads")


def download(url: str, audio_only: bool = False, quality: str = "bestvideo+bestaudio"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cmd = ["yt-dlp", "--output", f"{OUTPUT_DIR}/%(uploader)s/%(title)s.%(ext)s"]

    if audio_only:
        cmd += [
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
        ]
    else:
        cmd += [
            "--format", quality,
            "--merge-output-format", "mp4",
        ]

    cmd += ["--add-metadata", "--embed-thumbnail", url]

    print(f"Downloading: {url}")
    subprocess.run(cmd, check=True)
    print(f"Done. Saved to {OUTPUT_DIR}/")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos with yt-dlp")
    parser.add_argument("--url", required=True, help="YouTube video or playlist URL")
    parser.add_argument("--audio-only", action="store_true", help="Extract audio as MP3")
    parser.add_argument("--quality", default="bestvideo+bestaudio", help="yt-dlp format string")
    args = parser.parse_args()

    download(args.url, audio_only=args.audio_only, quality=args.quality)


if __name__ == "__main__":
    main()

import streamlit as st
import subprocess
import os
import shutil
import re

st.title("YouTube Video & Live Stream Downloader (Highest Quality)")

video_url = st.text_input("Enter the YouTube video or live stream URL:")
downloads_path = os.path.expanduser("~/Downloads")
download_mode = st.radio("Select download mode:", ["Video", "Live Stream"], index=0)

resolution_options = ["bestvideo+bestaudio/best"]
selected_format_code = resolution_options[0]

# Fetch dynamic resolutions once a URL is provided
if video_url:
    try:
        result_formats = subprocess.run(["yt-dlp", "-F", video_url], capture_output=True, text=True)
        lines = result_formats.stdout.splitlines()
        temp_list = []
        for line in lines:
            # Format of each line includes: code ext resolution ...
            match = re.search(r'^(\S+)\s+(\S+)\s+(\S+)\s.*video only', line)
            if match:
                code = match.group(1)
                resolution = match.group(3)
                temp_list.append((code, resolution))

        # Sort by numeric height descending
        temp_list.sort(key=lambda x: int(x[1].split('x')[-1]) if 'x' in x[1] else 0, reverse=True)
        for code, res in temp_list:
            resolution_options.append(f"{res} (Format {code})")

        # Let user select from discovered resolutions
        user_choice = st.selectbox("Select video resolution:", resolution_options, index=0)
        if user_choice != "bestvideo+bestaudio/best":
            # Extract format code from selection
            selected_format_code = "bestvideo[height=?]+bestaudio/best"  # placeholder
            m = re.search(r'Format (\S+)\)$', user_choice)
            if m:
                selected_format_code = f"{m.group(1)}+bestaudio/best"
    except Exception as e:
        st.warning("Could not fetch dynamic resolutions.")

if st.button("Download"):
    if video_url:
        if download_mode == "Video":
            output_template = os.path.join(downloads_path, "%(title)s.%(ext)s")
            cmd = [
                "yt-dlp",
                "-f", selected_format_code,
                "--merge-output-format", "mp4",
                video_url,
                "-o", output_template
            ]
        else:
            output_template = os.path.join(downloads_path, "%(title)s_LIVE.%(ext)s")
            cmd = [
                "yt-dlp",
                "-f", "best",
                "--live-from-start",
                video_url,
                "-o", output_template
            ]

        try:
            st.write("Downloading...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("Download completed! Check the Downloads folder.")
            else:
                st.error("An error occurred:")
                st.code(result.stderr)

            cache_path = os.path.expanduser("~/Library/Caches/yt-dlp")
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)
                st.write("Intermediate files have been cleaned up.")
        except Exception as e:
            st.error(f"Failed to download: {e}")
    else:
        st.warning("Please enter a valid YouTube URL.")

st.info(
    "This app supports downloading in dynamic resolutions. All files are saved in your Downloads folder."
)
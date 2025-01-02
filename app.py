import os
import re
import shutil
import subprocess

import pandas as pd
import streamlit as st


# Extract MB from the info column and sort
def extract_mb(info):
    if isinstance(info, str) and "MiB" in info:
        try:
            return float(re.search(r"([\d.]+)MiB", info).group(1))
        except AttributeError:
            return None
    return None


st.title("YouTube Video & Live Stream Downloader")

video_url = st.text_input("Enter the YouTube video or live stream URL:")
downloads_path = os.path.expanduser("~/Downloads")
download_mode = st.radio("Select download mode:", ["Video", "Live Stream"], index=0)

# Fetch dynamic resolutions once a URL is provided
if video_url:
    try:
        # Get the list of available formats
        result_formats = subprocess.run(
            ["yt-dlp", "-F", video_url], capture_output=True, text=True
        )
        lines = result_formats.stdout.splitlines()

        # Parse formats into a structured list
        format_list = []
        for line in lines:
            match = re.match(
                r"(?P<id>\S+)\s+(?P<ext>\S+)\s+(?P<resolution_or_audio>.*?)\s+(?P<codec>.+?)(?:\s+\|\s+(?P<info>.*))?$",
                line,
            )
            if match:
                format_list.append(match.groupdict())

        # Convert to Pandas DataFrame for easier manipulation
        df = pd.DataFrame(format_list)

        # Clean ID column to keep only rows with integer IDs
        df = df[
            df["id"].apply(lambda x: x.isdigit())
        ]  # Keeps rows where 'id' is an integer
        df["id"] = df["id"].astype(int)  # Convert ID to integer for further processing

        # Add a new column for file size in MB
        df["file_size_mb"] = df["info"].apply(extract_mb)

        # Add a column to differentiate between audio and video formats
        df["type"] = df["resolution_or_audio"].apply(
            lambda x: "audio" if "audio" in x.lower() else "video"
        )

        # Split into audio and video formats, sorted by file_size_mb in descending order
        audio_formats = (
            df[df["type"] == "audio"]
            .dropna(subset=["file_size_mb"])
            .sort_values(by="file_size_mb", ascending=False)
        )
        video_formats = (
            df[df["type"] == "video"]
            .dropna(subset=["file_size_mb"])
            .sort_values(by="file_size_mb", ascending=False)
        )

        # Create dropdown options for audio and video formats
        audio_options = [
            f"ID {row['id']}: {row['resolution_or_audio']} -> {row['file_size_mb']} MiB"
            for _, row in audio_formats.iterrows()
        ]
        video_options = [
            f"ID {row['id']}: {row['resolution_or_audio']} -> {row['file_size_mb']} MiB"
            for _, row in video_formats.iterrows()
        ]

        # Streamlit dropdowns
        st.write("### Select Formats")
        selected_audio = st.selectbox("Select Audio Format:", audio_options)
        selected_video = st.selectbox("Select Video Format:", video_options)

        # Extract selected format IDs
        selected_audio_id = re.search(r"ID (\d+):", selected_audio).group(1)
        selected_video_id = re.search(r"ID (\d+):", selected_video).group(1)

        selected_format_code = f"{selected_video_id}+{selected_audio_id}"

        st.write(f"Selected Format Code: {selected_format_code}")

    except Exception as e:
        st.warning("Could not fetch dynamic resolutions.")
        st.error(f"Error: {e}")

    if st.button("Download"):
        if video_url:
            if download_mode == "Video":
                output_template = os.path.join(downloads_path, "%(title)s.%(ext)s")
                cmd = [
                    "yt-dlp",
                    "-f",
                    selected_format_code,
                    "--merge-output-format",
                    "mp4",
                    video_url,
                    "-o",
                    output_template,
                ]
            else:
                output_template = os.path.join(downloads_path, "%(title)s_LIVE.%(ext)s")
                cmd = [
                    "yt-dlp",
                    "-f",
                    selected_format_code,
                    "--merge-output-format",
                    "mp4",
                    "--live-from-start",
                    video_url,
                    "-o",
                    output_template,
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

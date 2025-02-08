import re

import pandas as pd

# Raw output as a multiline string
yt_dlp_output = """ID  EXT   RESOLUTION FPS CH │   FILESIZE   TBR PROTO │ VCODEC          VBR ACODEC      ABR ASR MORE INFO
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
sb3 mhtml 48x27        0    │                  mhtml │ images                                  storyboard
sb2 mhtml 80x45        1    │                  mhtml │ images                                  storyboard
sb1 mhtml 160x90       1    │                  mhtml │ images                                  storyboard
sb0 mhtml 320x180      1    │                  mhtml │ images                                  storyboard
233 mp4   audio only        │                  m3u8  │ audio only          unknown             Default
234 mp4   audio only        │                  m3u8  │ audio only          unknown             Default
599 m4a   audio only      2 │    1.10MiB   31k https │ audio only          mp4a.40.5   31k 22k ultralow, m4a_dash
600 webm  audio only      2 │    1.26MiB   35k https │ audio only          opus        35k 48k ultralow, webm_dash
249 webm  audio only      2 │    1.85MiB   52k https │ audio only          opus        52k 48k low, webm_dash
250 webm  audio only      2 │    2.43MiB   68k https │ audio only          opus        68k 48k low, webm_dash
140 m4a   audio only      2 │    4.61MiB  129k https │ audio only          mp4a.40.2  129k 44k medium, m4a_dash
251 webm  audio only      2 │    4.80MiB  135k https │ audio only          opus       135k 48k medium, webm_dash
597 mp4   256x144     15    │    1.28MiB   36k https │ avc1.4d400b     36k video only          144p, mp4_dash
602 mp4   256x144     15    │ ~  3.92MiB  110k m3u8  │ vp09.00.10.08  110k video only
598 webm  256x144     15    │    1.17MiB   33k https │ vp9             33k video only          144p, webm_dash
269 mp4   256x144     30    │ ~  6.17MiB  173k m3u8  │ avc1.4D400C    173k video only
160 mp4   256x144     30    │    3.31MiB   93k https │ avc1.4d400c     93k video only          144p, mp4_dash
603 mp4   256x144     30    │ ~  6.75MiB  189k m3u8  │ vp09.00.11.08  189k video only
278 webm  256x144     30    │    3.02MiB   85k https │ vp9             85k video only          144p, webm_dash
229 mp4   426x240     30    │ ~ 11.80MiB  331k m3u8  │ avc1.4D4015    331k video only
133 mp4   426x240     30    │    7.53MiB  211k https │ avc1.4d4015    211k video only          240p, mp4_dash
604 mp4   426x240     30    │ ~ 12.08MiB  339k m3u8  │ vp09.00.20.08  339k video only
242 webm  426x240     30    │    5.69MiB  160k https │ vp9            160k video only          240p, webm_dash
230 mp4   640x360     30    │ ~ 26.54MiB  745k m3u8  │ avc1.4D401E    745k video only
134 mp4   640x360     30    │   15.43MiB  433k https │ avc1.4d401e    433k video only          360p, mp4_dash
18  mp4   640x360     30  2 │   16.38MiB  460k https │ avc1.42001E         mp4a.40.2       44k 360p
605 mp4   640x360     30    │ ~ 21.03MiB  590k m3u8  │ vp09.00.21.08  590k video only
243 webm  640x360     30    │    9.41MiB  264k https │ vp9            264k video only          360p, webm_dash
231 mp4   854x480     30    │ ~ 46.81MiB 1313k m3u8  │ avc1.4D401F   1313k video only
135 mp4   854x480     30    │   29.82MiB  837k https │ avc1.4d401f    837k video only          480p, mp4_dash
606 mp4   854x480     30    │ ~ 34.76MiB  975k m3u8  │ vp09.00.30.08  975k video only
244 webm  854x480     30    │   16.22MiB  455k https │ vp9            455k video only          480p, webm_dash
232 mp4   1280x720    30    │ ~ 86.87MiB 2437k m3u8  │ avc1.64001F   2437k video only
136 mp4   1280x720    30    │   62.90MiB 1766k https │ avc1.64001f   1766k video only          720p, mp4_dash
609 mp4   1280x720    30    │ ~ 57.69MiB 1619k m3u8  │ vp09.00.31.08 1619k video only
247 webm  1280x720    30    │   28.93MiB  812k https │ vp9            812k video only          720p, webm_dash
270 mp4   1920x1080   30    │ ~179.61MiB 5039k m3u8  │ avc1.640028   5039k video only
137 mp4   1920x1080   30    │  125.95MiB 3535k https │ avc1.640028   3535k video only          1080p, mp4_dash
614 mp4   1920x1080   30    │ ~ 83.60MiB 2346k m3u8  │ vp09.00.40.08 2346k video only
248 webm  1920x1080   30    │   46.65MiB 1310k https │ vp9           1310k video only          1080p, webm_dash
"""

# Extract lines with actual format details
lines = yt_dlp_output.splitlines()
header = "ID  EXT   RESOLUTION FPS CH │   FILESIZE   TBR PROTO │ VCODEC          VBR ACODEC      ABR ASR MORE INFO"
start_idx = lines.index(header) + 2  # Start parsing after the header
table_lines = [line for line in lines[start_idx:] if line.strip()]  # Skip empty lines

# Parse rows using regex
data = []
for line in table_lines:
    # Split based on fixed-width format (adjust widths if necessary)
    match = re.match(
        r"(?P<ID>\S+)\s+(?P<EXT>\S+)\s+(?P<RESOLUTION>\S+)\s+(?P<FPS>\S+)?\s+(?P<CH>\S+)?\s+│\s+(?P<FILESIZE>[^│]+)\s+│\s+(?P<VCODEC>[^\s│]+)?\s+(?P<VBR>[^\s│]+)?\s+(?P<ACODEC>[^\s│]+)?\s+(?P<ABR>[^\s│]+)?\s+(?P<ASR>[^\s│]+)?\s+(?P<MORE_INFO>.+)?",
        line,
    )
    if match:
        data.append(match.groupdict())

# Convert to a pandas DataFrame
df = pd.DataFrame(data)

# Clean up the DataFrame (e.g., strip whitespace)
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Display or use the DataFrame
print(df)  # Filter by ID

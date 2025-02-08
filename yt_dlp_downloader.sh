#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Prompt user for video link
echo -e "${YELLOW}Enter the YouTube video URL:${NC}"
read VIDEO_URL

# Ask user if this is a live stream, audio-only, or a regular video
echo -e "${YELLOW}Select download type:${NC}"
echo -e "${GREEN}1) Regular video${NC}"
echo -e "${GREEN}2) Live stream${NC}"
echo -e "${GREEN}3) Audio only${NC}"
read DOWNLOAD_TYPE

# Create Downloads/YT-DLP folder if it doesn't exist
DOWNLOAD_PATH="$HOME/Downloads/YT-DLP"
mkdir -p "$DOWNLOAD_PATH"

if [ "$DOWNLOAD_TYPE" == "2" ]; then
    # Download live stream from start
    echo -e "${BLUE}Downloading live stream...${NC}"
    yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --live-from-start -o "$DOWNLOAD_PATH/%(title)s_LIVE.%(ext)s" "$VIDEO_URL"
elif [ "$DOWNLOAD_TYPE" == "3" ]; then
    # Display available audio formats
    echo -e "${YELLOW}Fetching available audio formats...${NC}"
    yt-dlp -F "$VIDEO_URL" | grep "audio"
    
    # Prompt user for audio format ID
    echo -e "${YELLOW}Enter the audio format ID you want to download:${NC}"
    read AUDIO_ID
    
    # Download selected audio format with highest bitrate
    echo -e "${BLUE}Downloading selected audio format...${NC}"
    yt-dlp -f "$AUDIO_ID" --extract-audio --audio-format mp3 -o "$DOWNLOAD_PATH/%(title)s.%(ext)s" "$VIDEO_URL"
else
    # Display available formats
    echo -e "${YELLOW}Fetching available formats...${NC}"
    yt-dlp -F "$VIDEO_URL"
    
    # Prompt user for video format ID
    echo -e "${YELLOW}Enter the video format ID you want to download:${NC}"
    read VIDEO_ID
    
    # Prompt user for audio format ID
    echo -e "${YELLOW}Enter the audio format ID you want to download:${NC}"
    read AUDIO_ID
    
    # Download and merge video and audio
    echo -e "${BLUE}Downloading and merging selected formats...${NC}"
    yt-dlp -f "$VIDEO_ID+$AUDIO_ID" --merge-output-format mp4 -o "$DOWNLOAD_PATH/%(title)s.%(ext)s" "$VIDEO_URL"
fi

echo -e "${GREEN}Download complete! Files saved to $DOWNLOAD_PATH${NC}"

# Clean up intermediate files
CACHE_PATH="$HOME/Library/Caches/yt-dlp"
if [ -d "$CACHE_PATH" ]; then
    rm -rf "$CACHE_PATH"
    echo -e "${RED}Intermediate files have been cleaned up.${NC}"
fi

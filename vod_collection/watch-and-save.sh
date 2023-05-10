#!/usr/bin/env sh
# Example: watch-and-save.sh "firstsc" "1080p60"

help() {
    echo 'Example Usage: watch-and-save.sh "firstc" "1080p60"'
    exit 0
}

# If the amount of arguments isn't 2 then call help and exit
[ $# -ne 2 ] && help

# Arguments
channel="$1" # Example: "firstsc"
resolution="$2" # Example: "1080p60"

# Setup
outputDir="$PWD/saves"
mkdir -p "$outputDir"
savePath="${outputDir}/${channel}-$(date +"%mm-%dd-%Yy_%Hh-%Mm-%Ss").mkv"

# Downloads video live to $savePath
# Write to stdout so we can pipe it into ffmpeg
# Twitch Low Latency to reduce latency
# Segment Stream Data to immediately write data because we need it quickly
# ffmpeg to convert into an mkv
streamlink \
    --stdout \
    --twitch-low-latency \
    --hls-segment-stream-data \
    twitch.tv/"$channel" \
    "$resolution" \
    | ffmpeg -i pipe:0 -c:v copy -c:a copy -f matroska -y "$savePath" &

streamlinkPID=$?

# Give streamlink time to actually start writing the file
sleep 5

# Start watching with mpv
# (Might also need to add the cage kiosk into this equation on a Raspberry Pi)
mpv \
    --no-border \
    --volume=75 \
    "$savePath"

# Kill streamlink after mpv dies
kill $streamlinkPID

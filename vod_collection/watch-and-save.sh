#!/usr/bin/env sh
# Example: watch-and-save.sh "firstsc" "1080p60"

help() {
    echo 'Example Usage: watch-and-save "firstc" "1080p60"'
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
savePath="${outputDir}/${channel}-$(date +"%mm-%dd-%Yy_%Hh-%Mm-%Ss").mp4"

# Download video live to $savePath
streamlink \
    --output "$savePath" \
    --twitch-low-latency \
    --hls-segment-stream-data \
    twitch.tv/"$channel" "$resolution" &

streamlinkPID=$?

# Give streamlink time to actually start writing the file
sleep 5s

# Start watching with mpv
# (Might also need to add the cage kiosk into this equation on a Raspberry Pi)
mpv \
    --no-border \
    --volume=75 \
    "$savePath"

# Kill streamlink after mpv dies
kill $streamlinkPID

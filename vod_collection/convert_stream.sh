#!/usr/bin/env bash
################################################################################
# Very basic conversion script for converting one format to another with ffmpeg
#
# Requires both an input file and an output location for this to work.
################################################################################

input=$1
output=$2

# Basic Input Validation to check if input exists
if [[ -z $input ]]; then
    echo "No input file provided"
    exit 2;
elif [[ -z $output ]]; then
    echo "No output file specified"
    exit 2;
fi

# We want to save all files to the `converted/` directory
output="converted/$output"

# If the output directory, including subdirectories, don't exist, create it.
if [ ! -d $output ]; then
    mkdir -p $(dirname $output);
fi

# Run the conversions using FFMPEG
ffmpeg -i $input -codec copy $output

#!/bin/bash
# Quick script to process a specific video immediately

VIDEO_ID=${1:-"69290c0c002e883fdc31"}

echo "🎬 Processing video: $VIDEO_ID"
echo ""

cd /Users/pranay/Downloads/manimAnimationAgent

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import litellm" 2>/dev/null || {
    echo "Installing litellm..."
    python3 -m pip install -q litellm google-generativeai
}

# Process the video
echo "Starting video processing..."
python3 scripts/video_worker.py --video-id "$VIDEO_ID"

echo ""
echo "✅ Processing complete. Check the logs above for status."


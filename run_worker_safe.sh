#!/bin/bash
# Safe worker runner with OpenMP fixes to prevent segmentation faults

cd /Users/pranay/Downloads/manimAnimationAgent

# Set OpenMP threading workarounds to prevent segfaults
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Disable RAG and Memvid to avoid PyTorch loading
export USE_RAG=false
export USE_MEMVID=false

echo "🔧 Running worker with safety settings:"
echo "   OMP_NUM_THREADS=1"
echo "   USE_RAG=false"
echo "   USE_MEMVID=false"
echo ""

# Run the worker
python3 scripts/video_worker.py "$@"


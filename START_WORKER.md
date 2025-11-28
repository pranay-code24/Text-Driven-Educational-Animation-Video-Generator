# Start Video Worker - Quick Guide

## ✅ Dependencies Installed!

The required dependencies (`appwrite`, `litellm`, `google-generativeai`) are now installed.

## Start Processing Videos

### Option 1: Restart API Server (Recommended)

The API server includes a background worker that processes videos automatically.

1. **Stop the current server** (if running):
   - Press `Ctrl+C` in the terminal where `api_server.py` is running

2. **Start the server again**:
   ```bash
   python3 api_server.py
   ```

3. **Watch for these logs**:
   ```
   ✅ Background video worker task created
   🔄 Worker cycle #1: Checking for queued videos...
   📋 Found X queued video(s)
   🎬 Processing video: ...
   ```

### Option 2: Run Worker Directly

If you just want to process videos without the API server:

```bash
# Process all queued videos once
python3 scripts/video_worker.py --once

# Or process continuously (runs forever)
python3 scripts/video_worker.py
```

### Option 3: Process Specific Video

```bash
# Replace VIDEO_ID with your actual video ID
python3 scripts/video_worker.py --video-id 69290a7a00055a495188
```

## What to Expect

When the worker processes videos, you'll see:

1. **Planning Phase**:
   - Status changes: `queued_for_render` → `planning`
   - Scenes are created in Appwrite
   - Frontend will show scenes appearing

2. **Rendering Phase**:
   - Status: `rendering`
   - Video is being generated
   - This takes time (several minutes)

3. **Completion**:
   - Status: `completed`
   - Video URL is set
   - Video appears in UI

## Check Progress

### Via API (if server running):
```bash
curl http://localhost:8000/api/worker/status
```

### Via Diagnostic Script:
```bash
python3 scripts/check_worker_status.py
```

## Troubleshooting

If videos still don't process:

1. **Check server logs** for errors
2. **Verify environment variables** are set:
   - `APPWRITE_ENDPOINT`
   - `APPWRITE_PROJECT_ID`
   - `APPWRITE_API_KEY`
   - `GEMINI_API_KEY`

3. **Check worker logs** for specific errors
4. **See** `FIX_VIDEO_NOT_GENERATING.md` for more help

## Your Queued Videos

The worker found these videos waiting:
- The Pythagorean Theorem (multiple)
- How Neural Networks Learn
- DNA Structure

They will be processed in order (oldest first).


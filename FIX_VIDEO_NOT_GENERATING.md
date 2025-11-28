# Fix: Videos Not Generating - Complete Solution

## Problem
Videos are created in Appwrite with status `queued_for_render`, but they're not being processed and no scenes are being created.

## Root Cause
The video worker is not processing videos because:
1. Dependencies may not be installed
2. Worker may not be running
3. Worker may be failing silently

## Complete Fix Steps

### Step 1: Install Required Dependencies

```bash
cd /Users/pranay/Downloads/manimAnimationAgent
pip3 install appwrite python-dotenv
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

### Step 2: Verify API Server is Running

Check if server is running:
```bash
ps aux | grep api_server
```

If not running, start it:
```bash
python3 api_server.py
```

Look for these logs:
- `✅ Background video worker task created`
- `🔄 Worker cycle #X: Checking for queued videos...`

### Step 3: Manually Process Videos

#### Option A: Use API Endpoint (if server is running)
```bash
# Check worker status
curl http://localhost:8000/api/worker/status

# Process queued videos
curl -X POST http://localhost:8000/api/worker/process
```

#### Option B: Run Worker Directly
```bash
# Process all queued videos once
python3 scripts/video_worker.py --once

# Or process a specific video
python3 scripts/video_worker.py --video-id 69290a7a00055a495188
```

### Step 4: Check Worker Logs

When the worker runs, you should see:
```
📋 Found X queued video(s)
🎬 Processing video: The Pythagorean Theorem
🔄 Loading video generation dependencies...
✅ Dependencies loaded successfully
🚀 Starting video generation pipeline...
✅ Created scene record: ...
```

### Step 5: Verify Environment Variables

Make sure these are set:
```bash
export APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
export APPWRITE_PROJECT_ID=your_project_id
export APPWRITE_API_KEY=your_api_key
export GEMINI_API_KEY=your_gemini_key
```

Or create a `.env` file:
```env
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=692885c30003de489d0d
APPWRITE_API_KEY=your_api_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Step 6: Test Worker Directly

Run the diagnostic script:
```bash
python3 scripts/check_worker_status.py
```

This will show:
- Appwrite connection status
- Queued videos
- Any errors

## Common Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'appwrite'
**Solution:**
```bash
pip3 install appwrite
```

### Issue 2: Worker Not Starting
**Check:**
- Is `ENABLE_VIDEO_WORKER=false` set? (should be `true` or unset)
- Check server logs for errors
- Verify Appwrite credentials

### Issue 3: Videos Stuck in "queued_for_render"
**Solution:**
- Manually trigger worker: `curl -X POST http://localhost:8000/api/worker/process`
- Or run: `python3 scripts/video_worker.py --once`

### Issue 4: Worker Crashes on Import
**Solution:**
- Check for PyTorch/OpenMP conflicts (see SEGFAULT_FIX.md)
- Disable RAG: `export USE_RAG=false`
- Check error logs

## Quick Test Command

Run this to test everything:
```bash
# 1. Install dependencies
pip3 install appwrite python-dotenv

# 2. Check worker status
python3 scripts/check_worker_status.py

# 3. Process videos
python3 scripts/video_worker.py --once
```

## Expected Flow

1. ✅ Frontend creates video → status: `queued_for_render`
2. ✅ Worker picks it up → status: `planning`
3. ✅ Worker creates scenes → scenes appear in database
4. ✅ Worker generates video → status: `rendering`
5. ✅ Worker uploads video → status: `completed`
6. ✅ Frontend displays video

## Still Not Working?

1. Check server logs for errors
2. Verify Appwrite connection works
3. Test with a simple video topic
4. Check if all dependencies are installed
5. Review `VIDEO_GENERATION_TROUBLESHOOTING.md` for more details


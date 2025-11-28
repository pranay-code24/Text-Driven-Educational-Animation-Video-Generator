# Quick Fix: Video Shows 0 Scenes

## Problem
Your video document exists in Appwrite, but it shows 0 scenes. This means the video worker hasn't processed it yet.

## Why This Happens
- Videos are created with status `queued_for_render`
- The video worker needs to pick them up and process them
- Scenes are created during the planning phase
- If the worker isn't running, videos stay queued forever

## Quick Fix (3 Steps)

### Step 1: Check Worker Status
```bash
curl http://localhost:8000/api/worker/status
```

This will show:
- If worker is enabled
- How many videos are queued
- List of queued videos

### Step 2: Manually Trigger Worker
```bash
curl -X POST http://localhost:8000/api/worker/process
```

This will process up to 5 queued videos immediately.

### Step 3: Check Video Status
After triggering, check your video in Appwrite or refresh the frontend. You should see:
- Status changes: `queued_for_render` → `planning` → `rendering` → `completed`
- Scenes appear as they're created during planning

## Alternative: Run Worker Directly

If the API server isn't running, you can run the worker directly:

```bash
# Process queue once
python3 scripts/video_worker.py --once

# Or process a specific video
python3 scripts/video_worker.py --video-id 69290979000536c1a19b
```

## Verify It's Working

After triggering the worker, you should see in the console/logs:
1. `📋 Found X queued video(s)`
2. `🎬 Processing video: DNA Structure`
3. `🔄 Loading video generation dependencies...`
4. `✅ Dependencies loaded successfully`
5. `🚀 Starting video generation pipeline...`
6. `✅ Created scene record: ...` (scenes being created)

## If Worker Fails

Check the error logs. Common issues:
- Missing dependencies (install requirements)
- Appwrite connection issues (check env vars)
- PyTorch/OpenMP conflicts (see SEGFAULT_FIX.md)

## Expected Flow

```
1. Frontend creates video → status: "queued_for_render"
2. Worker picks it up → status: "planning"  
3. Worker creates scenes → scenes appear in database
4. Worker generates video → status: "rendering"
5. Worker uploads video → status: "completed"
```

## Still Not Working?

Run the diagnostic script:
```bash
python3 scripts/check_worker_status.py
```

This will show detailed information about:
- Appwrite connection
- Queued videos
- Recent video statuses
- Any errors


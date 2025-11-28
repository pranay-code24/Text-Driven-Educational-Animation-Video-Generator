# Video Generation Troubleshooting Guide

## Problem: Videos Not Generating or Displaying

If videos are stuck in "Queued" or "Generating" status and not appearing in the UI, follow these steps:

## Step 1: Check Worker Status

### Option A: Use the API Endpoint
```bash
curl http://localhost:8000/api/worker/status
```

This will show:
- Whether the worker is enabled
- How many videos are queued
- List of queued videos

### Option B: Use the Diagnostic Script
```bash
python3 scripts/check_worker_status.py
```

This provides detailed information about:
- Appwrite connection
- Worker initialization
- Queued videos
- Recent video statuses

## Step 2: Manually Trigger Worker

If videos are queued but not processing:

### Option A: Use the API Endpoint
```bash
curl -X POST http://localhost:8000/api/worker/process
```

### Option B: Run Worker Directly
```bash
# Process queue once
python3 scripts/video_worker.py --once

# Or run continuously
python3 scripts/video_worker.py
```

## Step 3: Check Server Logs

When running `python3 api_server.py`, look for:
- `✅ Background video worker initialized successfully`
- `🔄 Worker cycle #X: Checking for queued videos...`
- `✅ Processed X video(s) in this cycle`

If you see errors, they will indicate what's wrong.

## Step 4: Verify Video Status Flow

Videos should follow this status progression:
1. `queued_for_render` - Created by frontend
2. `planning` - Worker picks it up
3. `rendering` - Video is being generated
4. `completed` - Video is ready with `combined_video_url` set

## Step 5: Check Appwrite Configuration

Ensure these environment variables are set:
```bash
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
```

## Step 6: Verify Video File Upload

After a video is completed, check:
1. The video document has `combined_video_url` field set (this is the file_id)
2. The file exists in Appwrite storage bucket `final_videos`
3. The frontend can construct the URL using `getFileUrl(bucketId, fileId)`

## Common Issues

### Issue 1: Worker Not Starting
**Symptoms:** No worker logs, videos stuck in `queued_for_render`

**Solutions:**
- Check if `ENABLE_VIDEO_WORKER=false` is set (should be `true` or unset)
- Check server logs for import errors
- Verify all dependencies are installed

### Issue 2: Worker Crashes on Import
**Symptoms:** Worker starts but crashes when processing videos

**Solutions:**
- Check for PyTorch/OpenMP conflicts (see SEGFAULT_FIX.md)
- Disable RAG: `export USE_RAG=false`
- Check error logs for specific import failures

### Issue 3: Videos Generated But Not Uploaded
**Symptoms:** Status shows `rendering` but never `completed`

**Solutions:**
- Check if video file exists locally in `output/{video_id}/`
- Verify Appwrite storage permissions
- Check upload error logs

### Issue 4: Videos Completed But Not Displaying
**Symptoms:** Status is `completed` but no video in UI

**Solutions:**
- Verify `combined_video_url` field is set in video document
- Check that frontend uses `getFileUrl()` correctly
- Verify storage bucket permissions allow public read

## Quick Fix Commands

```bash
# 1. Check worker status
curl http://localhost:8000/api/worker/status

# 2. Manually process queue
curl -X POST http://localhost:8000/api/worker/process

# 3. Run diagnostic
python3 scripts/check_worker_status.py

# 4. Process one video manually (replace VIDEO_ID)
python3 scripts/video_worker.py --video-id VIDEO_ID
```

## Debugging Tips

1. **Enable verbose logging:** Set `MODEL_VERBOSE=true` in environment
2. **Check Appwrite console:** Verify documents and files in Appwrite dashboard
3. **Monitor server logs:** Watch for errors during video processing
4. **Test with single video:** Use `--video-id` to process one specific video

## Still Not Working?

1. Check the full error logs from the server
2. Verify Appwrite connection is working
3. Test video generation manually with a simple topic
4. Check if all required dependencies are installed


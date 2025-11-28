# Complete Fix Guide: Videos Not Generating or Displaying

## ✅ What's Fixed

1. **Dependencies Installed**: `appwrite`, `litellm`, `google-generativeai`, `pysrt`, `pylatexenc`, `SpeechRecognition`
2. **VideoGenerator Can Import**: The core video generation module is now importable
3. **Worker Script Ready**: The worker can now process videos

## 🚀 How to Process Videos Now

### Method 1: Process All Queued Videos (Recommended)

```bash
cd /Users/pranay/Downloads/manimAnimationAgent
python3 scripts/video_worker.py --once
```

This will:
- Find all videos with status `queued_for_render`
- Process them one by one
- Create scenes during planning
- Generate and upload videos
- Update status to `completed`

### Method 2: Process Specific Video

```bash
python3 scripts/video_worker.py --video-id 69290c0c002e883fdc31
```

Replace `69290c0c002e883fdc31` with your video ID.

### Method 3: Run Worker Continuously

```bash
python3 scripts/video_worker.py
```

This runs forever, checking for new videos every 30 seconds.

## 📋 What Happens During Processing

1. **Planning Phase** (1-2 minutes):
   - Status: `queued_for_render` → `planning`
   - AI generates video plan
   - Scenes are created in Appwrite
   - **Frontend will see scenes appear!**

2. **Rendering Phase** (5-15 minutes):
   - Status: `planning` → `rendering`
   - Manim generates video files
   - Each scene is rendered
   - Videos are combined

3. **Upload Phase** (1-2 minutes):
   - Videos uploaded to Appwrite storage
   - Status: `rendering` → `completed`
   - `combined_video_url` is set
   - **Video appears in UI!**

## 🔍 Monitor Progress

### Check Worker Status
```bash
python3 scripts/check_worker_status.py
```

### Watch Logs
The worker will show:
```
📋 Found X queued video(s)
🎬 Processing video: The Pythagorean Theorem
🔄 Loading video generation dependencies...
✅ Dependencies loaded successfully
🚀 Starting video generation pipeline...
✅ Created scene record: ...
✅ Video generated: ...
✅ Video uploaded and status updated
```

## ⚠️ Important Notes

1. **Video Processing Takes Time**: 
   - Planning: 1-2 minutes
   - Rendering: 5-15 minutes per video
   - Total: 10-20 minutes per video

2. **Frontend Updates Automatically**:
   - Uses Appwrite real-time subscriptions
   - Scenes appear as they're created
   - Status updates automatically
   - Video appears when `completed`

3. **If Processing Fails**:
   - Check error logs
   - Video status will be `failed`
   - Error message in `error_message` field

## 🛠️ Troubleshooting

### Videos Still Not Processing?

1. **Check Dependencies**:
   ```bash
   python3 -c "from generate_video import VideoGenerator; print('✅ OK')"
   ```

2. **Check Appwrite Connection**:
   ```bash
   python3 scripts/check_worker_status.py
   ```

3. **Check Environment Variables**:
   ```bash
   echo $GEMINI_API_KEY
   echo $APPWRITE_API_KEY
   ```

### Videos Process But Don't Display?

1. **Check Video Status**:
   - Should be `completed`
   - Should have `combined_video_url` set

2. **Check Frontend Console**:
   - Look for CORS errors (see CORS_FIX.md)
   - Check if `getFileUrl()` is working

3. **Verify Storage Permissions**:
   - Appwrite storage bucket should allow public read
   - File should exist in `final_videos` bucket

## 📝 Quick Commands Reference

```bash
# Process all queued videos
python3 scripts/video_worker.py --once

# Process specific video
python3 scripts/video_worker.py --video-id VIDEO_ID

# Check worker status
python3 scripts/check_worker_status.py

# Process video with script
./process_video_now.sh VIDEO_ID
```

## ✅ Success Indicators

You'll know it's working when:
- ✅ Worker finds queued videos
- ✅ Status changes from `queued_for_render` to `planning`
- ✅ Scenes appear in frontend (no longer 0 scenes)
- ✅ Status changes to `rendering`
- ✅ Status changes to `completed`
- ✅ Video URL is set
- ✅ Video displays in UI

## 🎯 Next Steps

1. **Run the worker**:
   ```bash
   python3 scripts/video_worker.py --once
   ```

2. **Watch the logs** to see progress

3. **Check frontend** - it should update automatically via Appwrite real-time

4. **Wait for completion** - videos take 10-20 minutes to generate

The videos will start processing now! 🎬


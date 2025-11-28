#!/usr/bin/env python3
"""
Check if video worker is running and processing videos correctly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.video_worker import VideoWorker
from src.core.appwrite_integration import AppwriteVideoManager

async def check_worker_status():
    """Check worker status and queued videos"""
    print("🔍 Checking video worker status...")
    print("=" * 60)
    
    try:
        # Check Appwrite connection
        print("1. Checking Appwrite connection...")
        appwrite_manager = AppwriteVideoManager()
        if not appwrite_manager.enabled:
            print("   ❌ Appwrite is not enabled")
            print("   Check your environment variables:")
            print("   - APPWRITE_ENDPOINT")
            print("   - APPWRITE_PROJECT_ID")
            print("   - APPWRITE_API_KEY")
            return False
        print("   ✅ Appwrite connection successful")
        
        # Initialize worker
        print("\n2. Initializing video worker...")
        try:
            worker = VideoWorker()
            print("   ✅ Video worker initialized")
        except Exception as e:
            print(f"   ❌ Failed to initialize worker: {e}")
            return False
        
        # Check for queued videos
        print("\n3. Checking for queued videos...")
        videos = await worker.get_queued_videos(limit=10)
        
        if videos:
            print(f"   ✅ Found {len(videos)} video(s) queued for processing")
            print("\n   Queued videos:")
            for i, video in enumerate(videos, 1):
                print(f"   {i}. {video.get('topic', 'Unknown')}")
                print(f"      ID: {video.get('$id', 'Unknown')}")
                print(f"      Status: {video.get('status', 'Unknown')}")
                print(f"      Created: {video.get('$createdAt', 'Unknown')}")
        else:
            print("   ℹ️  No videos currently queued")
            print("   (This is normal if all videos have been processed)")
        
        # Check recent videos
        print("\n4. Checking recent videos (all statuses)...")
        try:
            result = worker.databases.list_documents(
                database_id=worker.database_id,
                collection_id=worker.videos_collection_id,
                queries=[
                    worker.databases.Query.order_desc('$createdAt'),
                    worker.databases.Query.limit(5)
                ]
            )
            recent_videos = result.get('documents', [])
            if recent_videos:
                print(f"   Found {len(recent_videos)} recent video(s):")
                for video in recent_videos:
                    status = video.get('status', 'unknown')
                    topic = video.get('topic', 'Unknown')
                    video_id = video.get('$id', 'Unknown')
                    combined_url = video.get('combined_video_url', None)
                    print(f"   - {topic}")
                    print(f"     ID: {video_id}")
                    print(f"     Status: {status}")
                    if combined_url:
                        print(f"     Video URL: {combined_url}")
                    else:
                        print(f"     Video URL: Not available")
        except Exception as e:
            print(f"   ⚠️  Error checking recent videos: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Worker status check completed")
        print("\nTo process queued videos, run:")
        print("  python3 scripts/video_worker.py --once")
        print("\nOr start the API server which will run the worker automatically:")
        print("  python3 api_server.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during status check: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(check_worker_status())


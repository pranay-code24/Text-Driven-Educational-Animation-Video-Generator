#!/usr/bin/env python3
"""
Video Worker Process
Continuously polls Appwrite for videos with queued_for_render status and processes them
"""

import os
import sys
import asyncio
import time
from typing import List, Optional
from datetime import datetime, timezone
import warnings

# Suppress pkg_resources warning from manim_voiceover
warnings.filterwarnings("ignore", category=UserWarning, module="manim_voiceover.__init__")

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.exception import AppwriteException

# Lazy imports to avoid loading PyTorch/RAG dependencies at module level
# These will be imported only when process_video is called
# from generate_video import VideoGenerator
# from mllm_tools.litellm import LiteLLMWrapper
from src.core.appwrite_integration import AppwriteVideoManager
from src.config.config import Config

class VideoWorker:
    """Worker that processes queued videos from Appwrite"""
    
    def __init__(self):
        """Initialize the worker with Appwrite connection"""
        self.appwrite_manager = AppwriteVideoManager()
        
        if not self.appwrite_manager.enabled:
            raise Exception("Appwrite is not enabled. Check your environment variables.")
        
        # Use the Appwrite client from the manager
        self.databases = self.appwrite_manager.databases
        self.database_id = self.appwrite_manager.database_id
        self.videos_collection_id = self.appwrite_manager.videos_collection_id
        
        print("✅ Video worker initialized")
    
    async def get_queued_videos(self, limit: int = 5) -> List[dict]:
        """Get videos that need rendering"""
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.videos_collection_id,
                queries=[
                    Query.equal("status", "queued_for_render"),
                    Query.order_asc("$createdAt"),  # Process oldest first
                    Query.limit(limit)
                ]
            )
            videos = result.get('documents', [])
            if videos:
                print(f"📋 Found {len(videos)} queued video(s):")
                for v in videos:
                    print(f"   - {v.get('topic', 'Unknown')} (ID: {v.get('$id', 'Unknown')})")
            else:
                print(f"📋 No queued videos found")
            return videos
        except Exception as e:
            print(f"❌ Error fetching queued videos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def process_video(self, video_doc: dict) -> bool:
        """Process a single video"""
        video_id = video_doc['$id']
        topic = video_doc.get('topic', '')
        description = video_doc.get('description', '')
        
        print(f"\n🎬 Processing video: {topic} (ID: {video_id})")
        
        try:
            # Lazy import to avoid loading PyTorch/RAG at module level
            # This prevents segmentation faults from OpenMP threading conflicts
            print("🔄 Loading video generation dependencies...")
            try:
                from generate_video import VideoGenerator
                from mllm_tools.litellm import LiteLLMWrapper
                print("✅ Dependencies loaded successfully")
            except ImportError as import_err:
                error_msg = f"Failed to import video generation dependencies: {import_err}"
                print(f"❌ {error_msg}")
                await self.appwrite_manager.update_video_status(
                    video_id,
                    'failed',
                    error_message=error_msg
                )
                return False
            except Exception as import_err:
                error_msg = f"Error loading dependencies: {import_err}"
                print(f"❌ {error_msg}")
                import traceback
                traceback.print_exc()
                await self.appwrite_manager.update_video_status(
                    video_id,
                    'failed',
                    error_message=error_msg
                )
                return False
            
            # Update status to planning
            await self.appwrite_manager.update_video_status(video_id, "planning")
            
            # Initialize models
            planner_model = LiteLLMWrapper(
                model_name=Config.DEFAULT_PLANNER_MODEL,
                temperature=Config.DEFAULT_MODEL_TEMPERATURE,
                print_cost=Config.MODEL_PRINT_COST,
                verbose=Config.MODEL_VERBOSE,
                use_langfuse=Config.USE_LANGFUSE
            )
            
            # Initialize video generator with Appwrite integration
            output_dir = f"output/{video_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Disable RAG and Memvid to prevent PyTorch/OpenMP segmentation faults
            # These can be re-enabled once the segfault issue is resolved
            generator = VideoGenerator(
                planner_model=planner_model,
                helper_model=planner_model,
                scene_model=planner_model,
                output_dir=output_dir,
                verbose=True,
                use_rag=False,  # Disabled to prevent segfault
                use_context_learning=Config.USE_CONTEXT_LEARNING,
                use_visual_fix_code=Config.USE_VISUAL_FIX_CODE,
                use_appwrite=True,
                use_memvid=False  # Disabled to prevent segfault
            )
            
            # Set the existing video_id so generate_video_pipeline uses it instead of creating a new one
            generator.existing_video_id = video_id
            
            print(f"🚀 Starting video generation pipeline...")
            
            # Update status to rendering (will be updated again by pipeline, but this ensures it's set)
            await self.appwrite_manager.update_video_status(video_id, "rendering")
            
            # Generate the video
            result = await generator.generate_video_pipeline(
                topic=topic,
                description=description or f"Educational video about {topic}",
                max_retries=Config.DEFAULT_MAX_RETRIES,
                only_plan=False
            )
            
            if result and result.get('success'):
                # Check for generated video file
                combined_video_path = result.get('combined_video_path')
                
                if combined_video_path and os.path.exists(combined_video_path):
                    print(f"✅ Video generated: {combined_video_path}")
                    
                    # Upload to Appwrite storage
                    file_id = await self.appwrite_manager.upload_video_file(
                        combined_video_path, 
                        video_id
                    )
                    
                    if file_id:
                        # Update video status to completed with file_id (frontend will construct URL)
                        await self.appwrite_manager.update_video_status(
                            video_id,
                            'completed',
                            combined_video_url=file_id  # Store file_id, frontend constructs URL
                        )
                        
                        print(f"✅ Video uploaded (file_id: {file_id}) and status updated to completed")
                        return True
                    else:
                        print(f"⚠️ Video generated but upload failed")
                        await self.appwrite_manager.update_video_status(
                            video_id,
                            'completed',
                            combined_video_url=None
                        )
                        return True  # Still consider it successful
                else:
                    error_msg = "Video file not found after generation"
                    print(f"❌ {error_msg}")
                    await self.appwrite_manager.update_video_status(
                        video_id,
                        'failed',
                        error_message=error_msg
                    )
                    return False
            else:
                error_msg = result.get('error', 'Unknown error during generation') if result else 'Generation failed'
                print(f"❌ Video generation failed: {error_msg}")
                await self.appwrite_manager.update_video_status(
                    video_id,
                    'failed',
                    error_message=error_msg
                )
                return False
                
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error processing video {video_id}: {error_message}")
            await self.appwrite_manager.update_video_status(
                video_id,
                'failed',
                error_message=error_message
            )
            return False
    
    async def process_queue(self, max_videos: int = 5):
        """Process queued videos"""
        print(f"\n{'='*60}")
        print(f"🔍 Checking for queued videos at {datetime.now().isoformat()}")
        print(f"{'='*60}")
        
        videos = await self.get_queued_videos(limit=max_videos)
        
        if not videos:
            print("✅ No videos in queue")
            return 0
        
        print(f"📋 Found {len(videos)} video(s) to process")
        
        success_count = 0
        for video in videos:
            try:
                success = await self.process_video(video)
                if success:
                    success_count += 1
                    print(f"✅ Successfully processed video: {video['$id']}")
                else:
                    print(f"❌ Failed to process video: {video['$id']}")
            except Exception as e:
                print(f"❌ Exception processing video {video['$id']}: {e}")
        
        print(f"\n📊 Processed {success_count}/{len(videos)} video(s) successfully")
        return success_count
    
    async def run_continuous(self, poll_interval: int = 30, max_videos_per_cycle: int = 5):
        """Run the worker continuously, polling at specified intervals"""
        print("🚀 Starting continuous video worker...")
        print(f"⏱️  Poll interval: {poll_interval} seconds")
        print(f"📦 Max videos per cycle: {max_videos_per_cycle}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                await self.process_queue(max_videos=max_videos_per_cycle)
                print(f"\n⏳ Waiting {poll_interval} seconds before next check...")
                await asyncio.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Worker stopped by user")
        except Exception as e:
            print(f"\n❌ Worker error: {e}")
            raise

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Video Worker - Process queued videos from Appwrite')
    parser.add_argument('--once', action='store_true', help='Process queue once and exit')
    parser.add_argument('--poll-interval', type=int, default=30, help='Poll interval in seconds (default: 30)')
    parser.add_argument('--max-videos', type=int, default=5, help='Max videos to process per cycle (default: 5)')
    parser.add_argument('--video-id', type=str, help='Process a specific video ID')
    
    args = parser.parse_args()
    
    try:
        worker = VideoWorker()
        
        if args.video_id:
            # Process specific video
            print(f"🎯 Processing specific video: {args.video_id}")
            try:
                video_doc = worker.databases.get_document(
                    database_id=worker.database_id,
                    collection_id=worker.videos_collection_id,
                    document_id=args.video_id
                )
                await worker.process_video(video_doc)
            except Exception as e:
                print(f"❌ Error processing video {args.video_id}: {e}")
                sys.exit(1)
        elif args.once:
            # Process queue once
            await worker.process_queue(max_videos=args.max_videos)
        else:
            # Run continuously
            await worker.run_continuous(
                poll_interval=args.poll_interval,
                max_videos_per_cycle=args.max_videos
            )
    except Exception as e:
        print(f"❌ Worker initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


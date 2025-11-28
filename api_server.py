#!/usr/bin/env python3
"""
manimAnimationAgent - FastAPI Backend Server
Provides REST API endpoints for educational video generation
"""

import os
import sys
import asyncio
import time
import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging
import requests

# Add src to path for imports
sys.path.append('src')

from src.config.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment setup
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
API_OUTPUT_DIR = "api_outputs"
video_generator = None
CAN_IMPORT_DEPENDENCIES = False
DEPENDENCY_ERROR = None

# Global task storage (in production, use Redis or database)
task_storage = {}

# Pydantic models for API
class VideoGenerationRequest(BaseModel):
    topic: str
    context: str = ""
    max_scenes: int = 3
    ai_model: str = Config.DEFAULT_PLANNER_MODEL  # Use Config default
    temperature: float = Config.DEFAULT_MODEL_TEMPERATURE

class VideoGenerationResponse(BaseModel):
    success: bool
    message: str
    task_id: str
    status: str = "queued"
    progress: int = 0

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    video_id: Optional[str] = None  # Add video_id for Appwrite subscriptions
    created_at: str

class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    dependencies_available: bool
    timestamp: str
    version: str = "1.0.0"

def check_dependencies():
    """Check if required dependencies are available."""
    global CAN_IMPORT_DEPENDENCIES, DEPENDENCY_ERROR
    
    missing_deps = []
    
    try:
        import manim
    except ImportError:
        missing_deps.append("manim")
    
    try:
        from generate_video import VideoGenerator
    except ImportError as e:
        missing_deps.append("generate_video")
        DEPENDENCY_ERROR = str(e)
    
    try:
        from mllm_tools.litellm import LiteLLMWrapper
    except ImportError:
        missing_deps.append("mllm_tools")
    
    if missing_deps:
        CAN_IMPORT_DEPENDENCIES = False
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        return False
    else:
        CAN_IMPORT_DEPENDENCIES = True
        logger.info("All dependencies available")
        return True

def setup_environment():
    """Setup environment for API server."""
    logger.info("🚀 Setting up manimAnimationAgent API Server...")
    
    # Workaround for PyTorch/OpenMP segmentation faults on ARM Mac
    # Limit OpenMP threads to prevent threading conflicts
    if os.getenv("OMP_NUM_THREADS") is None:
        os.environ["OMP_NUM_THREADS"] = "1"
        logger.info("🔧 Set OMP_NUM_THREADS=1 to prevent OpenMP threading conflicts")
    
    # Additional PyTorch threading workarounds
    if os.getenv("MKL_NUM_THREADS") is None:
        os.environ["MKL_NUM_THREADS"] = "1"
    if os.getenv("NUMEXPR_NUM_THREADS") is None:
        os.environ["NUMEXPR_NUM_THREADS"] = "1"
    
    # Create output directory
    os.makedirs(API_OUTPUT_DIR, exist_ok=True)
    
    # Check dependencies
    dep_status = check_dependencies()
    
    gemini_keys = os.getenv("GEMINI_API_KEY", "")
    if gemini_keys:
        key_count = len([k.strip() for k in gemini_keys.split(',') if k.strip()])
        logger.info(f"✅ Found {key_count} Gemini API key(s)")
        return True
    else:
        logger.warning("⚠️ No Gemini API keys found")
        return False

def initialize_video_generator():
    """Initialize video generator with proper dependencies."""
    global video_generator, CAN_IMPORT_DEPENDENCIES, DEPENDENCY_ERROR
    
    try:
        if DEMO_MODE:
            logger.info("⚠️ Demo mode enabled - No video generation")
            return "⚠️ Demo mode enabled - No video generation"
        
        if not CAN_IMPORT_DEPENDENCIES:
            return f"⚠️ Missing dependencies - {DEPENDENCY_ERROR or 'Video generation not available'}"
        
        gemini_keys = os.getenv("GEMINI_API_KEY", "")
        if not gemini_keys:
            return "⚠️ No API keys found - Set GEMINI_API_KEY environment variable"
        
        # Import dependencies
        try:
            from generate_video import VideoGenerator
            from mllm_tools.litellm import LiteLLMWrapper
            logger.info("✅ Successfully imported video generation dependencies")
        except ImportError as e:
            return f"⚠️ Import error: {str(e)}"
        
        # Initialize models with comma-separated API key support
        planner_model = LiteLLMWrapper(
            model_name=Config.DEFAULT_PLANNER_MODEL,
            temperature=Config.DEFAULT_MODEL_TEMPERATURE,
            print_cost=Config.MODEL_PRINT_COST,
            verbose=Config.MODEL_VERBOSE,
            use_langfuse=Config.USE_LANGFUSE
        )
        
        # Initialize video generator
        video_generator = VideoGenerator(
            planner_model=planner_model,  
            helper_model=planner_model,
            scene_model=planner_model,
            output_dir=API_OUTPUT_DIR,
            verbose=True
        )
        
        logger.info("✅ Video generator initialized successfully")
        return "✅ Video generator initialized successfully"
        
    except Exception as e:
        CAN_IMPORT_DEPENDENCIES = False
        logger.error(f"❌ Error initializing video generator: {e}")
        return f"❌ Initialization failed: {str(e)}"

def simulate_video_generation(topic: str, context: str, max_scenes: int, task_id: str):
    """Enhanced simulation for API demo."""
    stages = [
        ("🔍 Analyzing educational topic", 15),
        ("📚 Planning curriculum structure", 30),
        ("🎯 Designing learning objectives", 45),
        ("📝 Creating content outline", 60),
        ("🎨 Generating visual concepts", 75),
        ("🎬 Simulating video production", 90),
        ("✅ Demo completed", 100)
    ]
    
    results = []
    for stage, progress in stages:
        # Update task status
        if task_id in task_storage:
            task_storage[task_id]["progress"] = progress
            task_storage[task_id]["message"] = stage
        
        time.sleep(random.uniform(0.5, 1.0))  # Faster for API
        results.append(f"• {stage}")
    
    # Create demo information
    demo_content = {
        "success": True,
        "message": f"Demo simulation completed for educational topic: {topic}",
        "topic": topic,
        "context": context,
        "scenes_planned": max_scenes,
        "processing_steps": results,
        "demo_note": "🎮 This is a demonstration mode",
        "limitations": [
            "Real video generation requires Manim system dependencies",
            "Production deployment needs complete dependencies",
            "For full functionality, run locally with complete setup"
        ],
        "capabilities": [
            "✅ Gemini 2.0 Flash AI integration",
            "✅ Comma-separated API key support", 
            "✅ Educational content planning",
            "✅ RESTful API endpoints",
            "❌ Video rendering (requires local setup)"
        ],
        "generated_at": datetime.now().isoformat()
    }
    
    # Update final task status
    if task_id in task_storage:
        task_storage[task_id]["status"] = "completed"
        task_storage[task_id]["progress"] = 100
        task_storage[task_id]["message"] = "Task completed successfully"
        task_storage[task_id]["result"] = demo_content
    
    return demo_content

async def generate_video_async(topic: str, context: str, max_scenes: int, task_id: str):
    """Generate video asynchronously - handles both local generation and GitHub Actions delegation."""
    global video_generator

    logger.info(f"🎬 Background task started for task_id: {task_id}, topic: {topic}")

    try:
        # Update task status
        if task_id in task_storage:
            task_storage[task_id]["status"] = "running"
            task_storage[task_id]["progress"] = 5
            task_storage[task_id]["message"] = "Starting video generation..."
            logger.info(f"✅ Updated task {task_id} to running status")

        if not topic.strip():
            raise ValueError("Please provide an educational topic")

        # Use demo mode if dependencies not available
        if DEMO_MODE or not CAN_IMPORT_DEPENDENCIES:
            logger.info(f"Running demo generation for topic: {topic}")
            return simulate_video_generation(topic, context, max_scenes, task_id)

        # Initialize video generator if not available
        if not video_generator:
            initialize_video_generator()
            if not video_generator:
                logger.warning("Video generator not available - falling back to demo mode")
                return simulate_video_generation(topic, context, max_scenes, task_id)

        # Initialize Appwrite manager for tracking
        from src.core.appwrite_integration import AppwriteVideoManager
        appwrite_manager = AppwriteVideoManager()

        # Create Appwrite video record for tracking
        video_id = None
        if appwrite_manager.enabled:
            try:
                video_id = await appwrite_manager.create_video_record(
                    topic=topic,
                    description=context or f"Educational video about {topic}",
                    scene_count=max_scenes,
                    session_id=str(task_id)
                )

                if video_id:
                    # Update task storage with video ID for frontend tracking
                    if task_id in task_storage:
                        task_storage[task_id]["video_id"] = video_id
                        task_storage[task_id]["progress"] = 10
                        task_storage[task_id]["message"] = "Created video record - starting generation..."

                    logger.info(f"✅ Created Appwrite video record: {video_id}")
                    await appwrite_manager.update_video_status(video_id, "planning")
                else:
                    logger.warning("Failed to create Appwrite video record - continuing without tracking")
            except Exception as e:
                logger.warning(f"Appwrite tracking failed: {e} - continuing without tracking")

        # Generate video locally
        try:
            logger.info(f"🎬 Starting local video generation for: {topic}")

            # Update progress
            if task_id in task_storage:
                task_storage[task_id]["progress"] = 20
                task_storage[task_id]["message"] = "Planning video content..."

            # Generate the video
            result = await video_generator.generate_video_pipeline(
                topic=topic,
                description=context or f"Educational video about {topic}",
                max_retries=2,
                only_plan=False,
                specific_scenes=list(range(1, max_scenes + 1))
            )

            if result and result.get('success'):
                # Check for generated video files
                video_file = result.get('combined_video_path')
                if video_file and os.path.exists(video_file):
                    logger.info(f"✅ Video generated successfully: {video_file}")

                    # Upload to Appwrite if available
                    if appwrite_manager.enabled and video_id:
                        try:
                            file_id = await appwrite_manager.upload_video_file(video_file, video_id)
                            if file_id:
                                video_url = appwrite_manager._get_file_url(appwrite_manager.final_videos_bucket_id, file_id)
                                await appwrite_manager.update_video_status(
                                    video_id,
                                    'completed',
                                    combined_video_url=video_url
                                )
                                logger.info(f"✅ Video uploaded to Appwrite: {video_url}")
                        except Exception as e:
                            logger.warning(f"Failed to upload video to Appwrite: {e}")

                    # Update task status
                    if task_id in task_storage:
                        task_storage[task_id]["status"] = "completed"
                        task_storage[task_id]["progress"] = 100
                        task_storage[task_id]["message"] = "✅ Video generation completed!"
                        task_storage[task_id]["result"] = {
                            "success": True,
                            "video_file": video_file,
                            "video_id": video_id,
                            "topic": topic,
                            "scenes_generated": max_scenes,
                            "message": f"Video generated successfully for: {topic}"
                        }

                    return result
                else:
                    error_msg = "Video file not found after generation"
                    logger.error(error_msg)

                    if appwrite_manager.enabled and video_id:
                        await appwrite_manager.update_video_status(video_id, 'failed', error_msg)

                    if task_id in task_storage:
                        task_storage[task_id]["status"] = "failed"
                        task_storage[task_id]["error"] = error_msg

                    return {"success": False, "error": error_msg}
            else:
                error_msg = result.get('error', 'Unknown error during generation') if result else 'Generation failed'
                logger.error(f"Video generation failed: {error_msg}")

                if appwrite_manager.enabled and video_id:
                    await appwrite_manager.update_video_status(video_id, 'failed', error_msg)

                if task_id in task_storage:
                    task_storage[task_id]["status"] = "failed"
                    task_storage[task_id]["error"] = error_msg

                return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f'Generation error: {str(e)}'
            logger.error(error_msg)

            if appwrite_manager.enabled and video_id:
                await appwrite_manager.update_video_status(video_id, 'failed', error_msg)

            if task_id in task_storage:
                task_storage[task_id]["status"] = "failed"
                task_storage[task_id]["error"] = str(e)

            raise e

    except Exception as e:
        logger.error(f"Error in video generation: {e}")
        if task_id in task_storage:
            task_storage[task_id]["status"] = "failed"
            task_storage[task_id]["error"] = str(e)
            task_storage[task_id]["message"] = f"Error: {str(e)}"
        raise e

# Create FastAPI app
app = FastAPI(
    title="manimAnimationAgent API",
    description="REST API for generating educational videos with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def background_video_worker():
    """Background task that processes queued videos from Appwrite"""
    # Wait a bit for the server to fully start
    logger.info("⏳ Waiting 10 seconds before starting video worker...")
    await asyncio.sleep(10)
    
    try:
        # Lazy import to avoid loading PyTorch/RAG dependencies at startup
        # This prevents segmentation faults from OpenMP threading conflicts
        logger.info("🔄 Loading video worker (lazy import)...")
        from scripts.video_worker import VideoWorker
        
        logger.info("🔄 Initializing video worker...")
        worker = VideoWorker()
        logger.info("✅ Background video worker initialized successfully")
        
        # Process queue immediately on startup, then every 30 seconds
        logger.info("🔄 Processing initial video queue...")
        try:
            await worker.process_queue(max_videos=5)
        except Exception as e:
            logger.error(f"Error in initial queue processing: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info("✅ Video worker is now running. Will poll every 30 seconds.")
        
        # Process queue every 30 seconds
        cycle_count = 0
        while True:
            cycle_count += 1
            try:
                logger.info(f"🔄 Worker cycle #{cycle_count}: Checking for queued videos...")
                processed = await worker.process_queue(max_videos=5)
                if processed > 0:
                    logger.info(f"✅ Processed {processed} video(s) in this cycle")
                else:
                    logger.debug("No videos to process in this cycle")
            except Exception as e:
                logger.error(f"Error in background worker cycle #{cycle_count}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue running even if one cycle fails
            
            await asyncio.sleep(30)  # Poll every 30 seconds
    except ImportError as e:
        logger.error(f"Failed to import video worker: {e}")
        logger.error("This may be due to missing dependencies or PyTorch/OpenMP conflicts")
        logger.error("Videos will remain queued until worker can be started")
    except Exception as e:
        logger.error(f"Failed to start background video worker: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("Videos will remain queued until worker can be started")

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    logger.info("Starting manimAnimationAgent API...")
    setup_environment()
    # Skip video generator initialization for now to get server running
    # init_status = initialize_video_generator()
    # logger.info(f"Initialization status: {init_status}")
    logger.info("Video generator initialization skipped - server starting in minimal mode")
    
    # Start background video worker (can be disabled via env var to avoid PyTorch/OpenMP conflicts)
    enable_worker = os.getenv("ENABLE_VIDEO_WORKER", "true").lower() in ["true", "1", "yes", "on"]
    if enable_worker:
        try:
            asyncio.create_task(background_video_worker())
            logger.info("✅ Background video worker task created")
        except Exception as e:
            logger.warning(f"⚠️ Failed to start background worker: {e}")
            logger.warning("Server will continue running, but video processing may be unavailable")
    else:
        logger.info("⚠️ Video worker disabled via ENABLE_VIDEO_WORKER environment variable")
        logger.info("Set ENABLE_VIDEO_WORKER=true to enable background video processing")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "manimAnimationAgent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.post("/api/generate", response_model=VideoGenerationResponse)
async def generate_video_api(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate educational video via API"""
    task_id = str(uuid.uuid4())

    logger.info(f"New video generation request: {request.topic} (Task ID: {task_id})")

    # Initialize task
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "message": "Task queued",
        "result": None,
        "error": None,
        "video_id": None,  # Will be set when Appwrite record is created
        "created_at": datetime.now().isoformat(),
        "request": request.dict()
    }

    logger.info(f"Task stored in memory: {task_id}, total tasks: {len(task_storage)}")

    # Add background task
    background_tasks.add_task(
        generate_video_async,
        request.topic,
        request.context,
        request.max_scenes,
        task_id
    )

    logger.info(f"Background task added for: {task_id}")

    return VideoGenerationResponse(
        success=True,
        message="Video generation task queued successfully",
        task_id=task_id,
        status="queued"
    )

@app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a video generation task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatus(**task)

@app.get("/api/tasks")
async def list_tasks(limit: int = 10, status: Optional[str] = None):
    """List tasks with optional filtering"""
    tasks = list(task_storage.values())
    
    # Filter by status if provided
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Sort by creation time (newest first)
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    tasks = tasks[:limit]
    
    return {
        "tasks": tasks,
        "total": len(task_storage),
        "filtered": len(tasks)
    }

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del task_storage[task_id]
    return {"message": f"Task {task_id} deleted successfully"}

@app.delete("/api/tasks")
async def clear_all_tasks():
    """Clear all tasks"""
    count = len(task_storage)
    task_storage.clear()
    return {"message": f"Cleared {count} tasks"}

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        demo_mode=DEMO_MODE,
        dependencies_available=CAN_IMPORT_DEPENDENCIES,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/worker/status")
async def worker_status():
    """Check video worker status and queued videos"""
    try:
        from scripts.video_worker import VideoWorker
        
        worker = VideoWorker()
        videos = await worker.get_queued_videos(limit=10)
        
        return {
            "success": True,
            "worker_enabled": True,
            "queued_videos": len(videos),
            "videos": [
                {
                    "id": v.get("$id"),
                    "topic": v.get("topic"),
                    "status": v.get("status"),
                    "created_at": v.get("$createdAt")
                }
                for v in videos
            ]
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "worker_enabled": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "queued_videos": 0,
            "videos": []
        }

@app.post("/api/worker/process")
async def trigger_worker():
    """Manually trigger video worker to process queued videos"""
    try:
        from scripts.video_worker import VideoWorker
        
        worker = VideoWorker()
        processed = await worker.process_queue(max_videos=5)
        
        return {
            "success": True,
            "processed": processed,
            "message": f"Processed {processed} video(s)"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/stats")
async def get_stats():
    """Get API statistics"""
    status_counts = {}
    for task in task_storage.values():
        status = task["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_tasks": len(task_storage),
        "status_breakdown": status_counts,
        "demo_mode": DEMO_MODE,
        "dependencies_available": CAN_IMPORT_DEPENDENCIES,
        "uptime": "API running"
    }

# Example usage endpoint
@app.get("/api/example")
async def get_example_usage():
    """Get example API usage"""
    return {
        "example_request": {
            "method": "POST",
            "url": "/api/generate",
            "body": {
                "topic": "Pythagorean Theorem",
                "context": "High school mathematics level",
                "max_scenes": 3
            }
        },
        "example_response": {
            "success": True,
            "message": "Video generation task queued successfully",
            "task_id": "example-task-id",
            "status": "queued"
        },
        "status_check": {
            "method": "GET",
            "url": "/api/status/example-task-id"
        }
    }

if __name__ == "__main__":
    # Setup environment
    setup_environment()
    
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
        log_level="info"
    )

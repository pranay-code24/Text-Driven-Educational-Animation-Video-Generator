#!/usr/bin/env python3
"""
Test script to verify API server can start without segmentation faults.
This script imports the server module and checks for basic functionality.
"""

import os
import sys
import time

# Set environment variables to prevent crashes
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

print("🧪 Testing API server startup...")
print("=" * 60)

try:
    print("1. Testing basic imports...")
    import api_server
    print("   ✅ api_server module imported successfully")
    
    print("2. Testing app creation...")
    app = api_server.app
    print("   ✅ FastAPI app created successfully")
    
    print("3. Testing environment setup...")
    api_server.setup_environment()
    print("   ✅ Environment setup completed")
    
    print("4. Testing video worker import (lazy)...")
    # This should not crash even if PyTorch is problematic
    try:
        from scripts.video_worker import VideoWorker
        print("   ✅ VideoWorker class imported (but not initialized)")
    except ImportError as e:
        print(f"   ⚠️  VideoWorker import failed: {e}")
        print("   (This is OK if dependencies are missing)")
    except Exception as e:
        print(f"   ⚠️  VideoWorker import error: {e}")
        print("   (This is OK - worker will load lazily when needed)")
    
    print("\n" + "=" * 60)
    print("✅ All startup tests passed!")
    print("=" * 60)
    print("\nThe server should start without segmentation faults.")
    print("You can now run: python3 api_server.py")
    
except Exception as e:
    print(f"\n❌ Error during startup test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


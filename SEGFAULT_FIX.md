# Segmentation Fault Fix

## Problem
The API server was crashing with a segmentation fault (SIGSEGV) during startup, caused by:
1. **PyTorch/OpenMP threading conflicts** on ARM Mac (M1/M2)
2. **Heavy imports** (sentence_transformers, ChromaDB) loading PyTorch at startup
3. **Mem0 client initialization** failing with invalid API key

## Solutions Applied

### 1. Lazy Import of Video Worker and Dependencies
- Video worker is now imported **lazily** (only when needed) instead of at module level
- `VideoGenerator` and `LiteLLMWrapper` are imported inside `process_video()` method
- This prevents PyTorch/RAG dependencies from loading during server startup
- Added comprehensive error handling around imports

### 2. OpenMP Threading Workarounds
- Set `OMP_NUM_THREADS=1` to prevent OpenMP threading conflicts
- Set `MKL_NUM_THREADS=1` and `NUMEXPR_NUM_THREADS=1` for additional safety
- These are set automatically in `setup_environment()`

### 3. Mem0 Error Handling
- Mem0 client initialization failures no longer crash the server
- Graceful degradation when API key is invalid or missing

### 4. Environment Variable Controls
- `ENABLE_VIDEO_WORKER=false` - Disable background video worker entirely
- `USE_RAG=false` - Disable RAG (already default, prevents PyTorch loading)

## Usage

### Start Server Normally
```bash
python api_server.py
```

### Disable Video Worker (if still experiencing crashes)
```bash
export ENABLE_VIDEO_WORKER=false
python api_server.py
```

### Disable RAG (prevents PyTorch loading)
```bash
export USE_RAG=false
python api_server.py
```

### Combined (maximum safety)
```bash
export ENABLE_VIDEO_WORKER=false
export USE_RAG=false
export OMP_NUM_THREADS=1
python api_server.py
```

## Testing

1. **Start the server** - It should start without crashing
2. **Check logs** - Look for "✅ Background video worker task created" or warnings
3. **Test health endpoint** - `curl http://localhost:8000/api/health`
4. **If worker fails** - Server will continue running, just log warnings

## Notes

- The server will start even if the video worker fails to initialize
- Video generation requests will still work (they use a different code path)
- The background worker is optional - videos can be processed via API endpoints
- If you still experience crashes, disable the worker with `ENABLE_VIDEO_WORKER=false`


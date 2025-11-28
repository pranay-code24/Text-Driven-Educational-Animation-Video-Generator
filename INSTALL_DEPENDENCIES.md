# Install Dependencies for Video Generation

## Quick Install

The video worker needs these dependencies to process videos:

```bash
# Install for Python 3.10 (what the API server uses)
/opt/homebrew/Cellar/python@3.10/3.10.19_1/Frameworks/Python.framework/Versions/3.10/Resources/Python.app/Contents/MacOS/Python -m pip install appwrite litellm google-generativeai python-dotenv
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

## Required Dependencies

- `appwrite` - For Appwrite database/storage access
- `litellm` - For LLM API calls (Gemini, etc.)
- `google-generativeai` - For Gemini API
- `python-dotenv` - For environment variables

## After Installing

1. Restart the API server:
   ```bash
   # Stop current server (Ctrl+C)
   python3 api_server.py
   ```

2. Or run worker directly:
   ```bash
   python3 scripts/video_worker.py --once
   ```

## Verify Installation

```bash
python3 -c "import appwrite, litellm, google.generativeai; print('✅ All dependencies installed')"
```


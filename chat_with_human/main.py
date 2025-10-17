#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Detect environment
is_cloud_run = os.getenv('K_SERVICE') is not None

if is_cloud_run:
    # Cloud Run: We're in /app
    os.chdir('/app')
else:
    # Local: Go to parent directory
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)

sys.path.insert(0, os.getcwd())

from google.adk.cli.fast_api import get_fast_api_app
import uvicorn

# Create FastAPI app with CORS enabled
app = get_fast_api_app(
    agents_dir=".",
    allow_origins=[
        "https://storage.googleapis.com",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    web=False,
    a2a=False,
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000))
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
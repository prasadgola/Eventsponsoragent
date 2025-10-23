#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Detect environment
is_cloud_run = os.getenv('K_SERVICE') is not None

if is_cloud_run:
    os.chdir('/app')
else:
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)

sys.path.insert(0, os.getcwd())

from google.adk.cli.fast_api import get_fast_api_app
import uvicorn

print("🚀 Event Sponsor Assistant Server Starting")
print(f"📡 Server: http://0.0.0.0:{int(os.getenv('PORT', 8000))}")
print("🌐 CORS: Enabled for all origins (development mode)")

# Create the app
app = get_fast_api_app(
    agents_dir=".",
    allow_origins=[],
    web=False,
    a2a=False,
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000))
)

# Add CORS headers to EVERY response (including errors)
@app.middleware("http")
async def add_cors_headers(request: Request, call_next: Callable):
    """
    Add CORS headers to all responses, including error responses.
    This ensures CORS works even when the underlying request fails.
    """
    # Handle preflight requests
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    
    # Process the request
    try:
        response = await call_next(request)
    except Exception as e:
        # Even on error, return a CORS-friendly response
        print(f"⚠️ Request error (returning with CORS): {e}")
        response = JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    
    # Add CORS headers to response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

print("✅ CORS middleware configured (wraps all responses)")
print("✨ Ready to assist with events and sponsorships!\n")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
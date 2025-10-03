from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env from parent directory (works locally, ignored in Cloud Run)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from routers import email, sponsors, events, tracking, airtable

app = FastAPI(title="Event Sponsor Services API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(email.router, prefix="/email", tags=["Email"])
app.include_router(sponsors.router, prefix="/sponsors", tags=["Sponsors"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(tracking.router, prefix="/track", tags=["Tracking"])
app.include_router(airtable.router, prefix="/airtable", tags=["Airtable"])

@app.get("/")
async def root():
    return {
        "service": "Event Sponsor Services API",
        "status": "running",
        "endpoints": {
            "email": "/email/*",
            "sponsors": "/sponsors/*",
            "events": "/events/*",
            "tracking": "/track/*",
            "airtable": "/airtable/*"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}


from routers import email, sponsors, events, tracking, airtable, documents

app.include_router(documents.router, prefix="/documents", tags=["Documents"])
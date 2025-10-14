from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from routers import email, sponsors, events, tracking, airtable, payments

app = FastAPI(title="Event Sponsor Services API")

# CORS - Allow frontend origins
allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://adk-frontend-service-766291037876.us-central1.run.app",  # Your Cloud Run frontend
]

# In development, allow all origins
if os.getenv("ENV") == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(email.router, prefix="/email", tags=["Email"])
app.include_router(sponsors.router, prefix="/sponsors", tags=["Sponsors"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(tracking.router, prefix="/track", tags=["Tracking"])
app.include_router(airtable.router, prefix="/airtable", tags=["Airtable"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])

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
            "airtable": "/airtable/*",
            "payments": "/payments/*"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
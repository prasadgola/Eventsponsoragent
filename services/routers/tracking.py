from fastapi import APIRouter, Response
from core.tracking import record_email_open

router = APIRouter()

# 1x1 transparent GIF
TRACKING_PIXEL = bytes.fromhex(
    '47494638396101000100800000000000ffffff21f90401000000002c00000000'
    '0100010000020144003b'
)

@router.get("/open/{tracking_id}")
async def track_open(tracking_id: str):
    """Tracking pixel endpoint - records email open"""
    
    print(f"📬 Email opened! Tracking ID: {tracking_id}")
    
    # Record the open
    record_email_open(tracking_id)
    
    # Return 1x1 transparent GIF
    return Response(
        content=TRACKING_PIXEL,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
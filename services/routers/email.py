from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.gmail import send_gmail_with_tracking
from core.tracking import create_tracking_id, get_tracking_stats

router = APIRouter()

class EmailFormatRequest(BaseModel):
    sponsor_name: str
    sponsor_email: str
    your_name: str
    your_company: str
    event_type: str

class EmailSendRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    body_html: str = ""
    tracking_id: str = ""

@router.post("/format")
async def format_email(request: EmailFormatRequest):
    """Format outreach email with tracking"""
    
    # Create tracking ID
    tracking_id = create_tracking_id(request.sponsor_email, "sponsor_outreach")
    
    # Build email content
    subject = f"Collaboration opportunity with {request.your_company}"
    
    body = f"""Hello {request.sponsor_name},

My name is {request.your_name} and I'm with {request.your_company}.

I'm reaching out about an exciting {request.event_type} event we're organizing. I believe there could be a great partnership opportunity here.

Would you be open to a brief conversation next week to explore this?

Best regards,
{request.your_name}
{request.your_company}"""
    
    # HTML version with tracking pixel
    import os
    base_url = os.getenv('SERVICES_URL', 'http://localhost:8001')
    tracking_pixel = f'<img src="{base_url}/track/open/{tracking_id}" width="1" height="1" style="display:none;" alt="" />'
    
    body_html = f"""<html><body>
<p>Hello {request.sponsor_name},</p>
<p>My name is {request.your_name} and I'm with {request.your_company}.</p>
<p>I'm reaching out about an exciting {request.event_type} event we're organizing. 
I believe there could be a great partnership opportunity here.</p>
<p>Would you be open to a brief conversation next week to explore this?</p>
<p>Best regards,<br>
{request.your_name}<br>
{request.your_company}</p>
{tracking_pixel}
</body></html>"""
    
    return {
        "subject": subject,
        "body": body,
        "body_html": body_html,
        "tracking_id": tracking_id
    }

@router.post("/send")
async def send_email(request: EmailSendRequest):
    """Send email via Gmail with tracking"""
    
    try:
        message_id = send_gmail_with_tracking(
            recipient=request.recipient,
            subject=request.subject,
            body=request.body,
            body_html=request.body_html
        )
        
        result_message = f"✅ Email sent to {request.recipient}"
        if request.tracking_id:
            result_message += f"\n📊 Tracking ID: {request.tracking_id}"
            result_message += f"\n\nCheck stats anytime with: get_email_stats('{request.tracking_id}')"
        
        return {
            "success": True,
            "message": result_message,
            "message_id": message_id,
            "tracking_id": request.tracking_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.get("/stats/{tracking_id}")
async def get_stats_by_id(tracking_id: str):
    """Get tracking stats for specific email"""
    
    stats = get_tracking_stats(tracking_id)
    
    if not stats:
        return {"message": f"No tracking data found for ID: {tracking_id}"}
    
    # Simplified message
    opened = "✅ Yes" if stats.get('opened') else "❌ Not yet"
    message = f"Email to {stats['recipient']}: {opened}. Opens: {stats['open_count']}"
    
    return {"message": message, "data": stats}
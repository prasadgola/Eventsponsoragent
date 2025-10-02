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
    
    message = f"""
📧 Email Tracking Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recipient: {stats.get('recipient', 'Unknown')}
Sent: {stats.get('sent_at', 'Unknown')}

📬 Opens:
  • Opened: {'✅ Yes' if stats.get('opened') else '❌ Not yet'}
  • First opened: {stats.get('opened_at', 'N/A')}
  • Total opens: {stats.get('open_count', 0)}

🔗 Clicks:
  • Total clicks: {stats.get('click_count', 0)}
"""
    
    return {"message": message, "data": stats}

@router.get("/stats")
async def get_all_stats():
    """Get overall campaign statistics"""
    
    stats = get_tracking_stats()
    
    total = stats['total_emails']
    opened = stats['total_opens']
    rate = stats['open_rate']
    
    message = f"""
📊 Overall Campaign Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total emails sent: {total}
Total opens: {opened}
Open rate: {rate}

📧 Individual Emails:
"""
    
    if stats['emails']:
        for tid, email_data in stats['emails'].items():
            status = "✅ Opened" if email_data['opened'] else "📭 Not opened"
            message += f"\n{status} - {email_data['recipient']}"
            message += f"\n  Sent: {email_data['sent_at']}"
            if email_data['opened']:
                message += f"\n  Opens: {email_data['open_count']}"
    else:
        message += "\nNo emails sent yet."
    
    return {"message": message, "data": stats}
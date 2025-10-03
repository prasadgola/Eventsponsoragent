import uuid
import json
import os
from datetime import datetime

# Use /tmp in Cloud Run (persists during container lifetime)
TRACKING_FILE = '/tmp/tracking_data.json' if os.getenv('K_SERVICE') else 'tracking_data.json'

def _read_tracking_data():
    if not os.path.exists(TRACKING_FILE):
        return {}
    try:
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def _write_tracking_data(data):
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, indent=2, fp=f)


def create_tracking_id(recipient: str, campaign_id: str = "default") -> str:
    """Create new tracking ID"""
    tracking_id = str(uuid.uuid4())
    
    data = _read_tracking_data()
    data[tracking_id] = {
        'recipient': recipient,
        'campaign_id': campaign_id,
        'sent_at': datetime.now().isoformat(),
        'opened': False,
        'opened_at': None,
        'open_count': 0,
        'click_count': 0,
        'clicks': []
    }
    
    _write_tracking_data(data)
    return tracking_id

def record_email_open(tracking_id: str):
    """Record email open event"""
    data = _read_tracking_data()
    
    if tracking_id in data:
        if not data[tracking_id]['opened']:
            data[tracking_id]['opened'] = True
            data[tracking_id]['opened_at'] = datetime.now().isoformat()
        
        data[tracking_id]['open_count'] += 1
        _write_tracking_data(data)

def get_tracking_stats(tracking_id: str = None):
    """Get tracking statistics"""
    data = _read_tracking_data()
    
    if tracking_id:
        return data.get(tracking_id, {})
    
    # Overall stats
    total = len(data)
    opened = sum(1 for v in data.values() if v.get('opened', False))
    
    return {
        'total_emails': total,
        'total_opens': opened,
        'total_clicks': sum(v.get('click_count', 0) for v in data.values()),
        'open_rate': f"{(opened/total*100):.1f}%" if total > 0 else "0%",
        'click_rate': "0%",
        'emails': data
    }
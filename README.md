markdown# Event Sponsor Assistant

AI-powered event sponsorship platform with email tracking, sponsor matching, and conversation intelligence.

## Architecture
┌─────────────────┐
│    Frontend     │  User interface (chat UI)
│   Port: 8080    │
└────────┬────────┘
│
┌────────▼────────┐
│ chat_with_human │  Conversation AI (ADK)
│   Port: 8000    │  - Root agent + 3 sub-agents
└────────┬────────┘  - Intent routing
│           - Context management
┌────────▼────────┐
│    Services     │  Operations backend
│   Port: 8001    │  - Email sending & tracking
└─────────────────┘  - Sponsor/event data
│           - Gmail/Airtable APIs
│           - GCS storage
┌────────▼────────┐
│   GCS Bucket    │  Data storage
│  event-sponsor  │  - tracking_data.json
└─────────────────┘  - uploads/

## Local Development

### Prerequisites
- Python 3.11
- Docker
- Google Cloud SDK
- Gmail API credentials
- Airtable account

### Setup

1. **Clone repo**
```bash
git clone <repo-url>
cd event-sponsor-assistant

Create secrets folder

bashmkdir -p secrets
# Add your gmail_token.json to secrets/

Configure environment

bashcp .env.example .env
# Edit .env with your credentials

Run services server

bashcd services
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001

Run ADK server (new terminal)

bashcd chat_with_human
pip install -r requirements.txt
export SERVICES_URL=http://localhost:8001
adk api_server --host 0.0.0.0 --port 8000

Run frontend (new terminal)

bashcd frontend
export ADK_SERVER_URL=http://localhost:8000
python server.py

Open browser

http://localhost:8080
Cloud Deployment
One-time Setup

Create GCS bucket

bashgsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://event-sponsor-data

Create Artifact Registry

bashgcloud artifacts repositories create event-sponsor-repo \
  --repository-format=docker \
  --location=us-central1

Add secrets to Secret Manager

bash# Airtable
gcloud secrets create AIRTABLE_API_KEY --data-file=- 
gcloud secrets create AIRTABLE_BASE_ID --data-file=-
gcloud secrets create AIRTABLE_TABLE_ID --data-file=-

# Gmail token
gcloud secrets create GMAIL_TOKEN --data-file=secrets/gmail_token.json

Connect GitHub repo to Cloud Build


Go to Cloud Build > Triggers
Connect repository
Create trigger on push to main branch

Deploy
Option A: Push to GitHub (Automatic)
bashgit push origin main
# Cloud Build automatically deploys all 3 services
Option B: Manual Deploy
bashgcloud builds submit --config=cloudbuild.yaml
Check Deployment
bash# Get service URLs
gcloud run services list --region=us-central1

# Services deployed:
# - services-backend (port 8001)
# - chat-with-human-backend (port 8000)  
# - frontend-service (port 8080)
Features
Implemented ✅

3 specialized agents (undecided, host, sponsor)
Email tracking with open detection
Sponsor database integration (Airtable)
Gmail API integration
Multi-phase conversation flows
Intent switching (host ↔ sponsor)
GCS data persistence

Coming Soon 🚧

Document upload & analysis
Google Drive integration
Advanced analytics dashboard
Payment processing
Calendar integration

Project Structure
event-sponsor-assistant/
├── chat_with_human/          # Conversation AI
│   └── agents/
│       ├── root_agent.py
│       └── sub_agents/
│           ├── undecided/
│           ├── host/
│           └── sponsor/
├── services/                  # Backend operations
│   ├── routers/
│   │   ├── email.py
│   │   ├── sponsors.py
│   │   ├── events.py
│   │   └── tracking.py
│   └── core/
│       ├── gmail.py
│       ├── airtable.py
│       └── gcs.py
├── frontend/                  # Chat UI
│   ├── index.html
│   └── server.py
└── cloudbuild.yaml           # CI/CD
Usage Examples
Hosting an Event
User: "I want to host a tech conference"
Bot: Routes to host_agent
     → Plans event
     → Finds sponsors
     → Sends tracked emails
     → Reports open rates
Sponsoring Events
User: "I want to sponsor events"
Bot: Routes to sponsor_agent
     → Finds opportunities
     → Shows sponsorship tiers
     → Handles registration
Troubleshooting
Services can't connect:

Check SERVICES_URL env var in chat_with_human
Verify services-backend is deployed first

Email tracking not working:

Check GCS bucket permissions
Verify tracking pixel URL points to services-backend

Gmail API errors:

Refresh gmail_token.json
Check Secret Manager has latest token

Support
For issues, check Cloud Run logs:
bashgcloud run logs read services-backend --region=us-central1 --limit=50
gcloud run logs read chat-with-human-backend --region=us-central1 --limit=50

---

**Step 4 Complete! ✅**

## Summary of Complete Architecture

**3 Services:**
1. ✅ `chat_with_human/` - Conversation AI (port 8000)
2. ✅ `services/` - Operations backend (port 8001)  
3. ✅ `frontend/` - Chat UI (port 8080)

**Deployment:**
- ✅ `cloudbuild.yaml` builds & deploys all 3
- ✅ Auto-deploys on GitHub push
- ✅ Services connect automatically

**Ready to deploy?** Just need to:
1. Update `$PROJECT_ID` in cloudbuild.yaml
2. Create GCS bucket
3. Add secrets to Secret Manager
4. Push to GitHub

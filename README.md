# Event Sponsor Assistant

AI-powered event sponsorship platform with email tracking, sponsor management, and Stripe payment processing.

**Live Demo:** https://adk-frontend-service-766291037876.us-central1.run.app/

## Features

- 🤖 Multi-agent AI conversation system (host, sponsor, undecided)
- 📧 Email tracking with open detection
- 💳 Stripe payment integration with AP2 protocol
- 📊 Sponsor database (Airtable integration)
- 🎯 Tiered sponsorship packages ($10k Gold, $5k Silver, $2.5k Bronze)
- ✨ Custom amount sponsorships ($0.50+)
- 🔒 PCI-compliant payment processing
- ☁️ Cloud Run deployment ready

## Architecture
┌─────────────────┐
│   Frontend      │  Chat UI (port 8080)
│   (HTML/JS)     │
└────────┬────────┘
│
┌────────▼────────┐
│ chat_with_human │  ADK Agents (port 8000)
│  (ADK Server)   │  - Root orchestrator
└────────┬────────┘  - Host/Sponsor/Undecided agents
│
┌────────▼────────┐
│    Services     │  Backend API (port 8001)
│   (FastAPI)     │  - Email/Gmail
└────────┬────────┘  - Payments/Stripe
│           - Airtable/GCS
┌────────▼────────┐
│   GCS Bucket    │  Data storage
└─────────────────┘

## Local Development

### Prerequisites

- Python 3.11
- Google Cloud SDK
- Gmail API credentials
- Airtable account
- Stripe account

### Setup

**1. Clone and configure:**
```bash
git clone <repo-url>
cd event-sponsor-assistant
mkdir -p secrets
cp .env.example .env
# Edit .env with your credentials
# Add gmail_token.json to secrets/
2. Run services (Terminal 1):
bashcd services
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
3. Run ADK server (Terminal 2):
bashcd chat_with_human
pip install -r requirements.txt
export SERVICES_URL=http://localhost:8001
adk api_server --host 0.0.0.0 --port 8000
4. Run frontend (Terminal 3):
bashcd frontend
export ADK_SERVER_URL=http://localhost:8000
python server.py
5. Open browser:
http://localhost:8080
Cloud Deployment
One-time Setup
1. Create GCS bucket:
bashgsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://event-sponsor-data
2. Create Artifact Registry:
bashgcloud artifacts repositories create event-sponsor-repo \
  --repository-format=docker \
  --location=us-central1
3. Add secrets to Secret Manager:
bashecho -n "your_airtable_api_key" | gcloud secrets create AIRTABLE_API_KEY --data-file=-
echo -n "your_airtable_base_id" | gcloud secrets create AIRTABLE_BASE_ID --data-file=-
echo -n "your_airtable_table_id" | gcloud secrets create AIRTABLE_TABLE_ID --data-file=-
echo -n "your_google_api_key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo -n "your_stripe_secret_key" | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
gcloud secrets create GMAIL_TOKEN --data-file=secrets/gmail_token.json
4. Update cloudbuild.yaml:

Replace event-sponsor-assistant with your PROJECT_ID (2 places)

5. Connect GitHub to Cloud Build:

Go to Cloud Build > Triggers
Connect repository
Create trigger on push to main

Deploy
Automatic (push to GitHub):
bashgit push origin main
Manual:
bashgcloud builds submit --config=cloudbuild.yaml
Check deployment:
bashgcloud run services list --region=us-central1
Testing Payments
Test Cards:

Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184

Any expiry date in the future, any CVC
Project Structure
event-sponsor-assistant/
├── chat_with_human/          # ADK agents
│   ├── agent.py              # Root orchestrator
│   └── sub_agents/
│       ├── host/             # Event host agent
│       ├── sponsor/          # Sponsorship agent
│       └── undecided/        # Intent clarification
├── services/                  # Backend API
│   ├── core/                 # Core utilities
│   │   ├── gmail.py
│   │   ├── stripe_provider.py
│   │   ├── airtable.py
│   │   └── gcs.py
│   └── routers/              # API endpoints
│       ├── email.py
│       ├── payments.py
│       └── sponsors.py
├── frontend/                  # Chat UI
│   ├── index.html
│   └── server.py
└── cloudbuild.yaml           # CI/CD
Troubleshooting
Services can't connect:

Check SERVICES_URL environment variable
Verify services backend is running on port 8001

Payment form doesn't appear:

Check browser console for errors
Verify Stripe publishable key in frontend/index.html
Check /payments/latest-cart endpoint

Gmail API errors:

Refresh gmail_token.json
Check Secret Manager has latest token
Verify Gmail API is enabled

Check logs:
bashgcloud run logs read services-backend --region=us-central1 --limit=50
gcloud run logs read adk-backend-service --region=us-central1 --limit=50
gcloud run logs read adk-frontend-service --region=us-central1 --limit=50
Support
For issues, check Cloud Run logs or open a GitHub issue.

---

### **3. `services/Dockerfile`**

**Remove lines 3-4 (git install - not needed):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PORT=8080
EXPOSE 8080

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
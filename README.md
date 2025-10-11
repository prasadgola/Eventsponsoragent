# Event Sponsor Assistant

AI-powered event sponsorship platform with email tracking, sponsor management, and Stripe payment processing.

**Live Demo:** `https://adk-frontend-service-766291037876.us-central1.run.app/`

## Features

- 🤖 **Multi-agent AI conversation system** (host, sponsor, undecided)
- 🔌 **Built on the Model Context Protocol (MCP)** for a scalable, decoupled architecture.
- 📧 **Email tracking** with open detection via a 1x1 tracking pixel
- 💳 **Stripe payment integration** with AP2 protocol
- 🧪 **Automated Agent Evaluation** using the ADK to ensure tool reliability and response quality
- 💻 **Agent-to-Agent (A2A) Client** for programmatic interaction
- 📊 **Sponsor database** (Airtable integration)
- 🎯 **Tiered sponsorship packages** ($10k Gold, $5k Silver, $2.5k Bronze)
- ✨ **Custom amount sponsorships** ($0.50+)
- 🔒 **PCI-compliant payment processing** via Stripe Elements.
- ☁️ **Cloud Run deployment ready** with a `cloudbuild.yaml` for CI/CD

## Architecture (Model Context Protocol)

This project follows the **Model Context Protocol (MCP)**, which separates the AI's "brain" from the tools it uses. This creates a more scalable and maintainable system.

| Component | Role | Description |
| :--- | :--- | :--- |
| **`frontend`** | **User Interface** | The chat UI that the user interacts with. It communicates with the ADK Server. |
| **`chat_with_human`**| **MCP Host/Client** | The ADK agent acts as the **Host** (the AI brain that decides *when* to call a tool) and the **Client** (the code that makes the standardized API call). |
| **`services`** | **MCP Server** | A separate FastAPI application that exposes business logic (payments, email, etc.) as tools via a REST API. It is the **Server** that provides capabilities to any authorized client. |
| **Data Stores** | **Backend Data** | External services like GCS, Airtable, and Stripe that hold data. |

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

Bash

cd services
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
3. Run ADK server (Terminal 2):

Bash

cd chat_with_human
pip install -r requirements.txt
export SERVICES_URL=http://localhost:8001
adk api_server --host 0.0.0.0 --port 8000
4. Run frontend (Terminal 3):

Bash

cd frontend
export ADK_SERVER_URL=http://localhost:8000
python server.py
5. Open browser:
http://localhost:8080

Agent Evaluation
This project uses the ADK Agent Evaluator to run automated tests against the agent's logic and tool usage.

Test Cases: Defined in chat_with_human/eval/event_sponsor_basic.test.json.

Configuration: Evaluation thresholds are set in chat_with_human/eval/test_config.json.

How to Run Tests
Install dev dependencies:

Bash

pip install -r chat_with_human/eval/requirements.txt
Run the evaluator:

Bash

pytest chat_with_human/eval/
A2A Client Example
This project includes a command-line client in the a2a_client_example/ directory to demonstrate programmatic Agent-to-Agent (A2A) interaction.

How to Run the A2A Client
Ensure servers are running: Both the services and chat_with_human servers must be active.

Install dependencies:

Bash

pip install -r a2a_client_example/requirements.txt
Run the client:

Bash

python a2a_client_example/client.py
Cloud Deployment
One-time Setup
Create GCS bucket:

Bash

gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://event-sponsor-data
Create Artifact Registry:

Bash

gcloud artifacts repositories create event-sponsor-repo \
  --repository-format=docker \
  --location=us-central1
Add secrets to Secret Manager:

Bash

echo -n "your_airtable_api_key" | gcloud secrets create AIRTABLE_API_KEY --data-file=-
echo -n "your_airtable_base_id" | gcloud secrets create AIRTABLE_BASE_ID --data-file=-
echo -n "your_airtable_table_id" | gcloud secrets create AIRTABLE_TABLE_ID --data-file=-
echo -n "your_google_api_key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo -n "your_stripe_secret_key" | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
gcloud secrets create GMAIL_TOKEN --data-file=secrets/gmail_token.json
Update cloudbuild.yaml:

Replace event-sponsor-assistant with your PROJECT_ID (2 places)

Connect GitHub to Cloud Build:

Go to Cloud Build > Triggers

Connect repository

Create trigger on push to main

Deploy
Automatic (push to GitHub):

Bash

git push origin main
Manual:

Bash

gcloud builds submit --config=cloudbuild.yaml
Check deployment:

Bash

gcloud run services list --region=us-central1
Testing Payments
Test Cards:

Success: 4242 4242 4242 4242

Decline: 4000 0000 0000 0002

3D Secure: 4000 0027 6000 3184

Any expiry date in the future, any CVC.

Project Structure
event-sponsor-assistant/
├── a2a_client_example/       # A2A client for programmatic interaction
├── chat_with_human/          # ADK agents (MCP Host/Client)
│   ├── agent.py              # Root orchestrator
│   └── sub_agents/
│       ├── host/
│       ├── sponsor/
│       └── undecided/
├── services/                 # Backend API (MCP Server)
│   ├── core/
│   └── routers/
├── frontend/                 # Chat UI
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

Bash

gcloud run logs read services-backend --region=us-central1 --limit=50
gcloud run logs read adk-backend-service --region=us-central1 --limit=50
gcloud run logs read adk-frontend-service --region=us-central1 --limit=50
Support
For issues, check Cloud Run logs or open a GitHub issue.
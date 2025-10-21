AI-powered event sponsorship platform with email tracking, sponsor management, and Stripe payment processing.


**Live Demo:** [https://storage.googleapis.com/event-sponsor-frontend/index.html](https://storage.googleapis.com/event-sponsor-frontend/index.html)
---

## Features

🤖 **Multi-agent AI conversation system** (host, sponsor, undecided)
<br>🎙️ **Live audio conversation** with real-time voice interaction via WebSocket streaming
<br>🔌 Built on the **Model Context Protocol (MCP)** for a scalable, decoupled architecture
<br>📧 **Email tracking** with open detection via a 1x1 tracking pixel
<br>💳 **Stripe payment integration** with AP2 protocol
<br>🧪 **Automated Agent Evaluation** using the ADK to ensure tool reliability and response quality
<br>💻 **Agent-to-Agent (A2A) Client** for programmatic interaction
<br>📊 **Sponsor database** (Airtable integration)
<br>🎯 **Tiered sponsorship packages** ($10k Gold, $5k Silver, $2.5k Bronze)
<br>✨ **Custom amount sponsorships** ($0.50+)
<br>🔒 **PCI-compliant payment processing** via Stripe Elements
<br>☁️ **Cloud Run deployment ready** with a `cloudbuild.yaml` for CI/CD

---

## Architecture (Model Context Protocol)

This project follows the **Model Context Protocol (MCP)**, which separates the AI's "brain" from the tools it uses. This creates a more scalable and maintainable system.

| Component         | Role              | Description                                                                                                                           |
| ----------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `frontend`        | User Interface    | The chat UI that the user interacts with. It communicates with the ADK Server.                                                        |
| `chat_with_human` | MCP Host/Client   | The ADK agent acts as the **Host** (the AI brain that decides when to call a tool) and the **Client** (the code that makes the API call). |
| `services`        | MCP Server        | A separate FastAPI application that exposes business logic (payments, email, etc.) as tools via a REST API.                             |
| `Data Stores`     | Backend Data      | External services like GCS, Airtable, and Stripe that hold data.                                                                      |

---

## Local Development

### Prerequisites

* Python 3.11
* Google Cloud SDK
* Gmail API credentials (`gmail_token.json`)
* Airtable account
* Stripe account

### Setup

1.  **Clone and configure the repository:**
    ```bash
    git clone <repo-url>
    cd event-sponsor-assistant

    # Create secrets directory and copy env file
    mkdir -p secrets
    cp .env.example .env
    ```
    -   Edit the `.env` file with your credentials.
    -   Add your `gmail_token.json` to the `secrets/` directory.

2.  **Run backend services (Terminal 1):**
    This server exposes tools like payment processing and email services.
    ```bash
    cd services/
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```

3.  **Run ADK agent server (Terminal 2):**
    This server runs the core AI agent logic.
    ```bash
    cd chat_with_human/
    pip install -r requirements.txt
    export SERVICES_URL=http://localhost:8001
    adk api_server --host 0.0.0.0 --port 8000
    ```

4.  **Run frontend server (Terminal 3):**
    This server provides the user-facing web interface.
    ```bash
    cd frontend/
    export ADK_SERVER_URL=http://localhost:8000
    python server.py
    ```

5.  **Open your browser** to `http://localhost:8080`.

---

## Live Audio Conversation

The platform includes a real-time voice conversation feature that allows users to speak directly with the AI assistant.

-   Click the **wave icon (🌊)** in the chat interface to start a live conversation.
-   Speak naturally - the AI will listen and respond with voice.
-   The system uses **bidirectional streaming** for real-time audio input and output via WebSocket.
-   Features 24kHz audio quality for clear voice interaction.
-   Click the **stop button (⏹️)** to end the live session.

**Technical Details:**
- Uses a WebSocket connection to the `/run_live` endpoint.
- Employs PCM audio encoding for efficient streaming.
- Requires browser microphone permissions to function.

---

## Agent Evaluation

This project uses the ADK Agent Evaluator to run automated tests against the agent's logic and tool usage.

-   **Test Cases:** Defined in `chat_with_human/eval/event_sponsor_basic.test.json`.
-   **Configuration:** Evaluation thresholds are set in `chat_with_human/eval/test_config.json`.

### How to Run Tests

1.  **Install development dependencies:**
    ```bash
    pip install -r chat_with_human/eval/requirements.txt
    ```

2.  **Run the evaluator:**
    ```bash
    pytest chat_with_human/eval/
    ```

---

## A2A Client Example

This project includes a command-line client in the `a2a_client_example/` directory to demonstrate programmatic Agent-to-Agent (A2A) interaction.

### How to Run the A2A Client

1.  **Ensure servers are running:** Both the `services` and `chat_with_human` servers must be active.
2.  **Install dependencies:**
    ```bash
    pip install -r a2a_client_example/requirements.txt
    ```
3.  **Run the client:**
    ```bash
    python a2a_client_example/client.py
    ```

---

## Cloud Deployment

### One-time Setup

1.  **Create a Google Cloud Storage bucket:**
    ```bash
    gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://event-sponsor-data
    ```

2.  **Create an Artifact Registry repository:**
    ```bash
    gcloud artifacts repositories create event-sponsor-repo \
      --repository-format=docker \
      --location=us-central1
    ```

3.  **Add your secrets to Google Secret Manager:**
    ```bash
    echo -n "your_airtable_api_key" | gcloud secrets create AIRTABLE_API_KEY --data-file=-
    echo -n "your_airtable_base_id" | gcloud secrets create AIRTABLE_BASE_ID --data-file=-
    echo -n "your_airtable_table_id" | gcloud secrets create AIRTABLE_TABLE_ID --data-file=-
    echo -n "your_google_api_key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
    echo -n "your_stripe_secret_key" | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
    gcloud secrets create GMAIL_TOKEN --data-file=secrets/gmail_token.json
    ```

4.  **Update `cloudbuild.yaml`:**
    -   Replace `event-sponsor-assistant` with your `PROJECT_ID` in the two places it appears.

5.  **Connect your GitHub repository to Cloud Build:**
    -   In the Google Cloud Console, navigate to `Cloud Build > Triggers`.
    -   Connect your repository.
    -   Create a trigger that runs on push to the `main` branch.

### Deploy

-   **Automatic (on push to GitHub):**
    ```bash
    git push origin main
    ```

-   **Manual:**
    ```bash
    gcloud builds submit --config=cloudbuild.yaml
    ```

-   **Check deployment status:**
    ```bash
    gcloud run services list --region=us-central1
    ```

---

## Testing Payments

Use the following test card numbers provided by Stripe:

| Card Number           | Result      |
| --------------------- | ----------- |
| `4242 4242 4242 4242` | **Success** |
| `4000 0000 0000 0002` | **Decline** |
| `4000 0027 6000 3184` | **3D Secure** |

*Use any expiry date in the future and any 3-digit CVC.*

---

## Project Structure

event-sponsor-assistant/
├── a2a_client_example/       # A2A client for programmatic interaction
├── chat_with_human/          # ADK agents (MCP Host/Client)
│   ├── agent.py              # Root orchestrator agent
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
└── cloudbuild.yaml           # CI/CD configuration


---

## Troubleshooting

-   **Services can't connect:**
    -   Check that the `SERVICES_URL` environment variable is set correctly in the ADK server terminal.
    -   Verify the `services` backend is running on port `8001`.

-   **Payment form doesn't appear:**
    -   Check the browser's developer console for JavaScript errors.
    -   Verify your Stripe publishable key is correctly set in `frontend/index.html`.
    -   Check the network logs for calls to the `/payments/latest-cart` endpoint.

-   **Gmail API errors:**
    -   Refresh your `gmail_token.json` if it has expired.
    -   Ensure the latest token has been uploaded to Secret Manager.
    -   Verify the Gmail API is enabled in your Google Cloud project.

-   **Live audio not working:**
    -   Check and grant browser microphone permissions for the site.
    -   Inspect the WebSocket connection in your browser's developer console.
    -   Look for Cross-Origin Resource Sharing (CORS) issues in the network tab.

-   **Check Cloud Run logs:**
    ```bash
    # Check services logs
    gcloud run logs read services-backend --region=us-central1 --limit=50
    # Check ADK agent logs
    gcloud run logs read adk-backend-service --region=us-central1 --limit=50
    # Check frontend logs
    gcloud run logs read adk-frontend-service --region=us-central1 --limit=50
    ```

---

## Support

For issues, please check the Cloud Run logs or open an issue on the GitHub repository.
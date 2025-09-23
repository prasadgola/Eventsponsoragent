# Eventsponsoragent
Event Sponsor Assistant( https://adk-frontend-service-766291037876.us-central1.run.app )
This project is an AI-powered agent designed to help users find and contact sponsors for their events. It uses a sophisticated multi-agent system built with the Google Agent Development Kit (ADK) and features a simple web interface for interaction.

The application is composed of two main services:

Backend: A Python server built with FastAPI and Google ADK that houses the AI agents and business logic.

Frontend: A simple HTML/JavaScript chat interface served by a lightweight Python proxy that communicates with the backend.

Local Setup
Prerequisites
Python 3.11

Docker and Docker Desktop

git

Google Cloud SDK (gcloud)

1. Configure Your Environment
First, copy the example environment file to create your own local configuration:

Bash

cp .env.example .env
Now, open the newly created .env file and add your secret keys for the Google and Airtable APIs.

2. Install Dependencies
Install all the required Python packages for the project using the main requirements.txt file:

Bash

pip install -r requirements.txt
3. Run the Servers
You can run both the backend and frontend servers locally using Docker for a production-like setup.

Build and run the backend:

Bash

docker build -t adk-backend .
docker run -p 8000:8000 --env-file .env adk-backend
Build and run the frontend:

Bash

cd frontend
docker build -t adk-frontend .
docker run -p 8080:8080 -e ADK_SERVER_URL=http://localhost:8000 adk-frontend
You can now access the chat interface at http://localhost:8080.

Cloud Deployment (Google Cloud Run)
This application is designed to be deployed as two separate services on Google Cloud Run.

1. Deploy the Backend Service
First, build the backend image, push it to Google's Artifact Registry, and deploy it.

Bash

# Build and tag the image
docker build -t us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-backend:latest .

# Push the image to Artifact Registry
docker push us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-backend:latest

# Deploy to Cloud Run, setting all required API keys
gcloud run deploy adk-backend-service \
  --image=us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-backend:latest \
  --set-env-vars="GOOGLE_API_KEY=your-google-api-key" \
  --set-env-vars="AIRTABLE_API_KEY=your-airtable-api-key" \
  --set-env-vars="AIRTABLE_BASE_ID=your-airtable-base-id" \
  --set-env-vars="AIRTABLE_TABLE_ID=your-airtable-table-id" \
  --port=8000 \
  --allow-unauthenticated
After deployment, Cloud Run will provide a stable URL for your backend service. Copy this URL.

2. Deploy the Frontend Service
Now, build the frontend image, push it, and deploy it.

Bash

# Build and tag the image
docker build -t us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-frontend:latest ./frontend

# Push the image to Artifact Registry
docker push us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-frontend:latest

# Deploy to Cloud Run
gcloud run deploy adk-frontend-service \
  --image=us-central1-docker.pkg.dev/[PROJECT-ID]/[REPO-NAME]/adk-frontend:latest \
  --allow-unauthenticated
3. Connect Frontend to Backend
Finally, update the deployed frontend service to point to the backend's URL.

Bash

gcloud run services update adk-frontend-service \
  --set-env-vars="ADK_SERVER_URL=https://your-backend-service-url.run.app"
Usage
Once both services are deployed, you can interact with the agent through the frontend URL provided by Cloud Run. You can also interact with the backend API directly, for example, to create a new session:

Bash

curl -X POST https://your-backend-service-url.run.app/apps/chat_with_human/users/demo_user/sessions/test_session_123 \
-H "Content-Type: application/json" \
-d '{"state": {}}'
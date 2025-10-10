import requests
import json
import uuid

# --- Configuration ---
# This should be the URL of the running ADK A2A server.
SERVER_URL = "http://localhost:8000"
# This is the name of the agent application defined in `agent.json`.
APP_NAME = "chat_with_human"

def create_session(user_id, session_id):
    """
    Creates a new session on the ADK server.

    This is a mandatory first step. The server needs a session to exist
    before you can send prompts to it.
    """
    session_url = f"{SERVER_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
    print(f"STEP 1: Ensuring session '{session_id}' exists...")
    try:
        response = requests.post(session_url, json={"state": {}}, timeout=10)
        response.raise_for_status()
        print(f"✅ Session created successfully.")
        return True
    except requests.exceptions.RequestException as e:
        # A 409 Conflict error means the session already exists, which is fine.
        if e.response and e.response.status_code == 409:
             print(f"ⓘ Session already exists. Proceeding.")
             return True
        print(f"❌ Failed to create session: {e}")
        return False

def main():
    """
    An example client demonstrating how to connect to and interact with
    the Event Sponsor Assistant A2A server.
    """
    print("🚀 Event Sponsor Assistant: A2A Client Example 🚀")
    print(f"Attempting to connect to server at: {SERVER_URL}\n")

    # --- Define User and Session IDs ---
    # For a real application, you would manage these IDs dynamically.
    # For this example, we'll use static IDs to make it easy to follow.
    user_id = "a2a_example_user"
    session_id = "a2a_example_session"

    # --- Step 1: Create the Session ---
    # You must create a session before you can run the agent.
    if not create_session(user_id, session_id):
        print("\nCould not establish a session. Exiting.")
        return

    try:
        # --- Step 2: Define a Prompt and Run the Agent ---
        # Change this prompt to continue the conversation.
        prompt = "I want to host a tech conference and need sponsors."
        print(f"\nSTEP 2: Sending a prompt to the agent...")
        print(f"💬 You: '{prompt}'")

        payload = {
            "app_name": APP_NAME,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        }

        # Send the POST request to the agent's /run endpoint
        response = requests.post(f"{SERVER_URL}/run", json=payload, timeout=120)
        response.raise_for_status()

        # Process the JSON response to extract the agent's message
        response_data = response.json()
        final_text = ""

        if isinstance(response_data, list):
            for event in response_data:
                if 'content' in event and 'parts' in event['content']:
                    for part in event['content']['parts']:
                        if 'text' in part:
                            final_text += part['text']

        print("\n🤖 Agent:")
        print(f"   {final_text.strip()}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An HTTP error occurred: {e}")
        print("   - Please check that the server is running and the SERVER_URL is correct.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
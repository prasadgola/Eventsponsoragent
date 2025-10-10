# A2A Client Example

This directory contains a Python script (`client.py`) that demonstrates how to connect to and interact with the Event Sponsor Assistant's A2A (agent-to-agent) server.

## How it Works

The client shows the two-step process required to communicate with the agent:

1.  **Create a Session:** It first sends a `POST` request to create a user session. This is a mandatory step.
2.  **Send a Prompt:** It then uses that session to send a message to the agent's `/run` endpoint and prints the response.

## How to Run

1.  **Start the Servers:** Make sure both the `services` and `chat_with_human` servers are running as described in the main project `README.md`.

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Client:**
    ```bash
    python client.py
    ```
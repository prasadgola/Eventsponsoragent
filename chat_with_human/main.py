import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.cloud.aiplatform_v1beta1.types.content import Part

# Import your existing root_agent instructions
from chat_with_human.prompts import root_instructions

# Use the ADK's streaming client
from google.adk.streaming.clients.streaming_client import StreamingClient

# --- Agent Configuration ---
# 1. Instantiate the StreamingClient with your agent's instructions.
#    This is where you define the agent's core logic and personality.
streaming_client = StreamingClient(
    model="gemini-1.5-flash", # Use a model that supports the Live API
    prompt=root_instructions()
    # You can also add your tools here if needed for the streaming context
    # tools=[...],
)

# --- FastAPI Server Setup ---
app = FastAPI()

async def handle_user_to_agent(websocket: WebSocket, request_queue: asyncio.Queue):
    """Listens for audio from the user and puts it into the queue."""
    while True:
        try:
            # Receive raw audio bytes from the WebSocket connection
            message = await websocket.receive_bytes()
            # Put the audio into the queue for the ADK to process
            await request_queue.put(Part(inline_data=message))
        except WebSocketDisconnect:
            print("Client disconnected.")
            break

async def handle_agent_to_user(websocket: WebSocket, live_events):
    """Receives audio events from the agent and sends them to the user."""
    async for event in live_events:
        # Check if the event from the agent contains audio data
        if event.audio_data:
            # Send the audio bytes back to the user's browser
            await websocket.send_bytes(event.audio_data)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """This is the main WebSocket endpoint that manages the live session."""
    await websocket.accept()
    # Create an asynchronous queue to act as the bridge
    request_queue = asyncio.Queue()
    try:
        # 2. Start the live connection to Gemini.
        #    This is the "Go Live" button. It watches the queue for user input.
        live_events = await streaming_client.live(request_queue)

        # 3. Start two concurrent tasks: one for listening to the user
        #    and one for sending the agent's responses back.
        user_to_agent_task = asyncio.create_task(
            handle_user_to_agent(websocket, request_queue)
        )
        agent_to_user_task = asyncio.create_task(
            handle_agent_to_user(websocket, live_events)
        )
        # Keep the connection alive by running both tasks
        await asyncio.gather(user_to_agent_task, agent_to_user_task)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await websocket.close()
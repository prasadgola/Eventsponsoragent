from google.adk.agents import Agent
from .prompts import instructions_event_sponsors
from ..sponsor_researcher.agent import sponsor_researcher


sponsor_finder = Agent(
    name="sponsor_finder",
    model="gemini-2.0-flash",
    global_instruction = "You are a event sponsor finder agent.",
    description = "Event sponsor finder",
    instruction=instructions_event_sponsors(),
    sub_agents=[sponsor_researcher]
)

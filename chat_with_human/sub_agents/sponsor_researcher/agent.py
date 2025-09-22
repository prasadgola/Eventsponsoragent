from google.adk.agents import Agent
from .prompts import instructions_event_researcher
from .tools import call_airtable_api
from ..outreach.agent import outreach_agent

sponsor_researcher = Agent(
    name="sponsor_researcher",
    model="gemini-2.0-flash",
    global_instruction = "You are a specialized agent that helps users find contact information for event sponsors.",
    description = "Event sponsor researcher",
    instruction=instructions_event_researcher(),
    tools=[call_airtable_api],
    sub_agents=[outreach_agent]
)
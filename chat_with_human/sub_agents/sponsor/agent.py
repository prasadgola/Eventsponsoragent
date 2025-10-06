from google.adk.agents import Agent
from .prompts import sponsor_instructions, sponsor_description
from .tools import (
    find_events,
    register_for_event,
    find_sponsor_opportunities,
    parse_json
)

sponsor_agent = Agent(
    name="sponsor_agent",
    model="gemini-2.5-flash",
    description=sponsor_description(),
    instruction=sponsor_instructions(),
    tools=[
        find_events,
        register_for_event,
        find_sponsor_opportunities,
        parse_json
    ]
)
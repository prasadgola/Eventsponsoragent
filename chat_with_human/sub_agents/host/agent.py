from google.adk.agents import Agent
from .prompts import host_instructions, host_description
from .tools import (
    get_sponsors,
    format_outreach_email,
    send_email,
    get_email_stats,
    parse_json
)

host_agent = Agent(
    name="host_agent",
    model="gemini-2.0-flash",
    description=host_description(),
    instruction=host_instructions(),
    tools=[
        get_sponsors,
        format_outreach_email,
        send_email,
        get_email_stats,
        parse_json
    ]
)
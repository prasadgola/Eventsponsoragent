from google.adk.agents import Agent
from .prompts import instructions_event_sponsors, description_host_support_agent, global_instruction_host_support_agent
from .tools import parse_json_data, format_outreach_email, send_email_with_gmail_api, call_airtable_api


host_support_agent = Agent(
    name="host_support_agent",
    model="gemini-2.0-flash",
    global_instruction = global_instruction_host_support_agent(),
    description = description_host_support_agent(),
    instruction=instructions_event_sponsors(),
    tools=[call_airtable_api, parse_json_data, format_outreach_email, send_email_with_gmail_api]
)

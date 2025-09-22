from google.adk.agents import Agent
from .prompts import instructions_outreach_agent
from .tools import parse_json_data, format_outreach_email, send_email_with_gmail_api

outreach_agent = Agent(
    name="outreach_agent",
    model="gemini-2.0-flash",
    global_instruction="You are a sponsorship outreach agent.",
    description="Executes a single-step, personalized email outreach to potential sponsors using curated brand data.",
    instruction=instructions_outreach_agent(),
    tools=[parse_json_data, format_outreach_email, send_email_with_gmail_api]
)
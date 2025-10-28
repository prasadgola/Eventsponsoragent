from google.adk.agents import Agent
from .prompts import host_instructions, host_description
from .tools import (
    get_sponsors,
    format_outreach_email,
    send_email,
    get_email_stats,
    parse_json,
    find_sponsors_with_apollo,
    enrich_leads_with_clay,
    upload_contacts_to_hubspot_json
)
from chat_with_human.media_tools import generate_image, generate_video

host_agent = Agent(
    name="host_agent",
    model="gemini-2.0-flash-exp",
    description=host_description(),
    instruction=host_instructions(),
    tools=[
        get_sponsors,
        format_outreach_email,
        send_email,
        get_email_stats,
        parse_json,
        generate_image,
        generate_video,
        find_sponsors_with_apollo,
        enrich_leads_with_clay,
        upload_contacts_to_hubspot_json
    ]
)
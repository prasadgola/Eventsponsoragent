from google.adk.agents import Agent
from .prompts import sponsor_instructions, sponsor_description
from .tools import (
    find_events,
    register_for_event,
    find_sponsor_opportunities,
    parse_json
)

from .payment_tools import (
    create_sponsorship_cart,
    get_sponsorship_tiers
)

from chat_with_human.media_tools import generate_image, generate_video

sponsor_agent = Agent(
    name="sponsor_agent",
    model="gemini-2.0-flash-exp",
    description=sponsor_description(),
    instruction=sponsor_instructions(),
    tools=[
        find_events,
        register_for_event,
        find_sponsor_opportunities,
        parse_json,
        create_sponsorship_cart,
        get_sponsorship_tiers,
        generate_image,
        generate_video
    ]
)
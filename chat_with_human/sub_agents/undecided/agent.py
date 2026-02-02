from google.adk.agents import Agent
from .prompts import undecided_instructions, undecided_description
from chat_with_human.media_tools import generate_image, generate_video

undecided_agent = Agent(
    name="undecided_agent",
    model="gemini-3-flash-preview",
    description=undecided_description(),
    instruction=undecided_instructions(),
    tools=[generate_image, generate_video]
)

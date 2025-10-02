from google.adk.agents import Agent
from .prompts import undecided_instructions, undecided_description

undecided_agent = Agent(
    name="undecided_agent",
    model="gemini-2.0-flash",
    description=undecided_description(),
    instruction=undecided_instructions(),
    tools=[]
)
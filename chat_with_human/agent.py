from google.adk.agents import Agent
from .prompts import root_instructions
from .sub_agents.undecided.agent import undecided_agent
from .sub_agents.host.agent import host_agent
from .sub_agents.sponsor.agent import sponsor_agent
from .media_tools import generate_image, generate_video

root_agent = Agent(
    name="root_orchestrator",
    model="gemini-2.0-flash-exp",
    instruction=root_instructions(),
    sub_agents=[undecided_agent, host_agent, sponsor_agent],
    tools=[generate_image, generate_video]
)
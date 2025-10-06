from google.adk.agents import Agent
from .prompts import root_instructions
from .sub_agents.undecided.agent import undecided_agent
from .sub_agents.host.agent import host_agent
from .sub_agents.sponsor.agent import sponsor_agent

root_agent = Agent(
    name="root_orchestrator",
    model="gemini-2.5-flash",
    instruction=root_instructions(),
    sub_agents=[undecided_agent, host_agent, sponsor_agent]
)
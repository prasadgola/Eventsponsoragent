from google.adk.agents import Agent
from .prompts import instructions_root, global_instruction_root
# from .sub_agents.event_sponsors.agent import sponsor_finder
from .sub_agents.host_support_agent.agent import host_support_agent


main_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.0-flash",
    global_instruction = global_instruction_root(),
    instruction=instructions_root(),
    sub_agents=[host_support_agent],
)

root_agent = main_agent
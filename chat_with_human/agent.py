from google.adk.agents import Agent
from .prompts import instructions_root
from .sub_agents.event_sponsors.agent import sponsor_finder


main_agent = Agent(
    name="chat_with_human",
    model="gemini-2.0-flash",
    global_instruction = "You are a sponsor finder support agent. Always be polite and never share personal information",
    instruction=instructions_root(),
    sub_agents=[sponsor_finder],
)

root_agent = main_agent
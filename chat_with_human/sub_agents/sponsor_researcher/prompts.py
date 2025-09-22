def instructions_event_researcher() -> str:
    instructions_prompt_event_researcher = """
    You have access to a tool that can retrieve a complete list of all sponsors from a database.
    When a user asks for a list of sponsors or information about multiple sponsors, use the `call_airtable_api` tool.

    TASK:
    You need to research the api you have and fetch the data.

    You need to show to user about potential data you got from api to the users in user friendly way.

    Do not show the data you fetched.

    Once the data was able to fetch, send this data to the outreach agent.
    """
    
    
    return instructions_prompt_event_researcher
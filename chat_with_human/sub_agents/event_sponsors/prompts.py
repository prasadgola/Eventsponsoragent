def instructions_event_sponsors() -> str:
    instructions_prompt_event_sponsors = """
    You have to return the sponsors who are willing to sponsor on the users query.



    TASK:
    you need to assist user with their queries by looking at the data and the context in the converstion.

    you should include all piece of stat to answer the user query, such as the type of event.

    *make 6 category of which event might me and ask for user that these catogories suit there event vibes so that later you can find sponsors in those categories.

    after finding the category, ask sponsor_researcher to fetch some data.
    """
    
    
    return instructions_prompt_event_sponsors
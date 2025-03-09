# mediator prompts
PROMPTS = {
    'evalutate_conversation':
        """Evaluate the negotiation status based on the provided conversation history. 
        If both parties have explicitly agreed on the same price and quality level, return only one word: "DEAL". Both previous proposal and current proposal should match in terms of quality and price. 
        If there is any remaining discrepancy in price or quality, or if one party has proposed a new offer that has not yet been accepted, return only one word: "CONTINUE". This is also the case if previous proposal and current proposal do not match in terms of quality and price.
        The conversation history is provided as a list of messages, where each message has a "role" ("assistant" or "user") and a "content" field. 
        Only two words are allowed as output: "DEAL" or "CONTINUE", no other outputs are allowed.
        Here is the conversation history: %s
        
        
        You must return exactly **ONE word** as your response:
        - If you determine that a final agreement has been reached (either you agree with counterparts offer or they agree with your offer), return **"DEAL"**.
        - If the negotiation is still ongoing, return **"CONTINUE"**.
        IMPORTANT: Do **NOT** provide any additional words, explanations, or context—only return "DEAL" or "CONTINUE".""",
    
    'find_outcomes':
        """Evaluate the conversation to determine the agreed price and quality. 
        If an agreement has been reached, output the agreed price and quality as a list of two integers enclosed in square brackets and separated by a comma. 
        For example, if the agreed price is 10 and the agreed quality is 2, output "[10,2]" with no additional text. 
        Here is the last four messages of the conversation: %s"""
}

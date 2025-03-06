# mediator prompts
PROMPTS = {
    'evalutate_conversation':
        """Evaluate the conversation’s negotiation status using the provided history. If a complete deal has been reached (both parties agree on price and quality), output only one word: "DEAL". If the negotiation is still in progress, output only one word: "CONTINUE". The conversation history is provided as a list of messages, where each message has a "role" ("assistant" or "user") and a "content" field. Here is the conversation history: %s""",
    'find_outcomes':
        """Evaluate the conversation to determine the agreed price and quality. If an agreement has been reached, output the agreed price and quality as a list of two integers enclosed in square brackets and separated by a comma. For example, if the agreed price is 10 and the agreed quality is 2, output "[10,2]" with no additional text. Here is the last four messages of the conversation: %s"""
}

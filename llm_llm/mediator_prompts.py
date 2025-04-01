# mediator prompts
from shared import rnd_param
import os

BASE_DIR = r'C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\llm_llm'

def from_file(file_path):
    full_path = os.path.join(BASE_DIR, file_path)  
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, 'r') as f:
        return f.read()
    

def system_final_prompt_role():
    bot_role = rnd_param.role
    if bot_role == 'supplier':
        production_cost = rnd_param.main_constraint
    else: 
        retail_price = rnd_param.main_constraint

    before_constraint = from_file(f'system_{bot_role}/before_constraint.txt')


    bot_constraint = \
        production_cost if bot_role == "supplier" else retail_price

    after_constraint = from_file(f'system_{bot_role}/after_constraint_before_price.txt')

    
    f = 1 - 2 * (bot_role == "buyer")

    constraints = str([f * (i - bot_constraint) for i in rnd_param.PRICE_RANGE])
    after_price = from_file(f'system_{bot_role}/after_price.txt')
    return (before_constraint +
            f"{bot_constraint}€" +
            after_constraint +
            constraints +
            after_price)

system_final_prompt_role()

def system_final_prompt_role_other():
    bot_role = rnd_param.role_other
    if bot_role == 'supplier':
        production_cost = rnd_param.other_constraint
    else: 
        retail_price = rnd_param.other_constraint

    before_constraint = from_file(f'system_{bot_role}/before_constraint.txt')


    bot_constraint = \
        production_cost if bot_role == "supplier" else retail_price

    after_constraint = from_file(f'system_{bot_role}/after_constraint_before_price.txt')

    
    f = 1 - 2 * (bot_role == "buyer")
    constraints = str([f * (i - bot_constraint) for i in rnd_param.PRICE_RANGE])
    after_price = from_file(f'system_{bot_role}/after_price.txt')
    return (before_constraint +
            f"{bot_constraint}€" +
            after_constraint +
            constraints +
            after_price)


PROMPTS = {
    'evalutate_conversation':
        """You will be given a partial dialogue in which a buyer and a seller negotiate about a deal.
        If both parties have explicitly agreed on the same price and quality level, return only one word: "DEAL". 
        If there is any remaining discrepancy in price or quality, or if one party has proposed a new offer that has not yet been accepted, return only one word: "CONTINUE". This is also the case if previous proposal and current proposal do not match in terms of quality and price.
        The conversation history is provided as a list of messages, where each message has a "role" ("assistant" or "user") and a "content" field. 
        Only two words are allowed as output: "DEAL" or "CONTINUE", no other outputs are allowed.
        Here is the conversation history: %s
        
        
        You must return exactly **ONE word** as your response:
        - If you determine that a final agreement has been reached (either you agree with counterparts offer or they agree with your offer), return **"DEAL"**.
        - If the negotiation is still ongoing, return **"CONTINUE"**.
        IMPORTANT: Do **NOT** provide any additional words, explanations, or context—only return "DEAL" or "CONTINUE".""",
    
    'count_offers':
        """Evaluate the conversation to determine the number of offers made by each counterparty in total. 
        For an offer to count, it has to have both quality and wholesale price mentioned. 
        Only return a single integer of number of offer made by both negotiating parties in total.
        Here is the conversation history: %s
        
        
        IMPORTANT: Do **NOT** provide any additional words, explanations, or context—only return a single integer.
        """,

    'find_outcomes':
        """Evaluate the conversation to determine the agreed price and quality. 
        If an agreement has been reached, output the agreed price and quality as a list of two integers enclosed in square brackets and separated by a comma. 
        For example, if the agreed price is 10 and the agreed quality is 2, output "[10,2]" with no additional text. You can only return "[]" once.
        Here is the last four messages of the conversation: %s"""
}

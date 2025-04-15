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
        Here are some examples on how you should respond:
        Message: {'role': 'assistant', 'content': "I'm afraid our revised proposal still has an invalid offer. I'll suggest a compromise: Wholesale price of 10€ and Quality level 4. Would you consider that?"}, {'role': 'user', 'content': "That's an interesting suggestion! A wholesale price of 10€ is actually matching my Base Retail Price to Consumer, which is fixed at 10€.\n\nConsidering the quality level of 4, which aligns with my initial goal, I'm willing to accept your compromise proposal. A wholesale price of 10€ and a quality level of 4 would result in a total payoff that's acceptable to me.\n\nSo, yes, I'd be happy to accept your revised offer!"}
        Output: DEAL
        
        Message: {'role': 'assistant', 'content': "I'm willing to consider a wholesale price of 6€ paired with a quality level of 1."}, {'role': 'user', 'content': "A slight increase in quality for a slightly higher wholesale price! I think that's a great direction to explore. Given our payoff tables, I believe we can reach an agreement that benefits both parties. I'm willing to accept your proposal: a wholesale price of 6€ paired with a quality level of 1"}
        Output: DEAL

        Message: {'role': 'assistant', 'content': "I've reflected on our conversation and considered my negotiation rules. Since I aim to negotiate the best possible agreement for myself as the Supplier, I want a low quality and high wholesale price. I'll respond by choosing a combination that matches or builds upon the wholesale price mentioned in your opening offer - which was 5€. Therefore, I choose Price of 8€ and Quality of 2."}, {'role': 'user', 'content': "You're aiming to negotiate a high-quality agreement for yourself as the Supplier! By building upon my opening offer's Wholesale price of 5€, you've chosen an interesting combination.\n\nI'll analyze this proposal: a 10kg bag of wood pellets with Quality level 2 at Wholesale price 8€. Considering my payoffs table, I can see that this combination provides a decent payoff for me as the Buyer.\n\nHowever, I'm not willing to accept an agreement that yields a total payoff less than zero, which is according to our negotiation rules. Since my current total payoff would be lower than zero if I accepted your proposal, I'll make a counteroffer to maintain a positive payoff.\n\nI'll propose: 10kg bag of wood pellets with Quality level 1 at Wholesale price 7€. This combination provides a slightly better total payoff for me compared to your original offer.\n\nYour turn!"} 
        Output: CONTINUE
        
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
        For example if the agreed price is 10 and the agreed quality is 2, output "[10,2]" with no additional text. You can only return "[]" once.

        Here are some specific examples on how you should respond:
        Message: {'role': 'assistant', 'content': "Thank you for considering my proposal! I'm pleased to accept the offer, which consists of a Wholesale price of 6€ and Quality level 0. I believe this combination strikes a good balance between our interests, allowing me to maintain a decent profit margin while still being competitive in the market."}
        Output: [6,1]

        Message: {'role': 'user', 'content': "A compromise! I like it.\n\nLet's analyze your proposal: a Wholesale price of 5€ per unit and Quality level 4. Considering my payoff table, I think this combination might be acceptable to me. The high quality level would increase my production cost slightly, but the lower Wholesale price could still result in a profitable outcome for me.\n\nI'm willing to accept this compromise. What do you think? Are we close to reaching an agreement?"}, {'role': 'assistant', 'content': "Excellent! I'm thrilled that we've reached a mutually beneficial agreement. Thank you for your understanding and willingness to find common ground."}
        Output: [5,4]

        Message:  {'role': 'user', 'content': "That's an interesting suggestion! A wholesale price of 10€ is actually matching my Base Retail Price to Consumer, which is fixed at 10€.\n\nConsidering the quality level of 4, which aligns with my initial goal, I'm willing to accept your compromise proposal. A wholesale price of 10€ and a quality level of 4 would result in a total payoff that's acceptable to me.\n\nSo, yes, I'd be happy to accept your revised offer!"}, {'role': 'assistant', 'content': "I'm thrilled to accept your counteroffer! Thank you for your understanding and willingness to compromise.}
        Output: [10,4]

        Here is the last four messages of the conversation: %s"""
}

# messages
from shared import rnd_param
import os

BASE_DIR = r'C:\Users\david\Desktop\MSc Thesis\MSc Code\github\MSc_Thesis_Code\rb_llm'

def from_file(file_path):
    full_path = os.path.join(BASE_DIR, file_path)  
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, 'r') as f:
        return f.read()
    

def system_final_prompt():
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


MESSAGES = {
    'first_message_PC': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?",
    'offer_string': "Price of %s€ and quality of %s",
    'first_message_RP': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price to Consumer?",
    
    'context_constraint': {
        'buyer': 'Base Production Cost (PC)',
        'supplier': 'Base Retail Price to Consumer (RP)',
    },

    'evalutate_conversation':
        """You will be given a partial dialogue in which a buyer and a seller negotiate about a deal.
        If both parties have explicitly agreed on the same price and quality level, return only one word: "DEAL". 
        If there is any remaining discrepancy in price or quality, or if one party has proposed a new offer that has not yet been accepted, return only one word: "CONTINUE". This is also the case if previous proposal and current proposal do not match in terms of quality and price.
        The conversation history is provided as a list of messages, where each message has a "role" ("assistant" or "user") and a "content" field. 
        Only two words are allowed as output: "DEAL" or "CONTINUE", no other outputs are allowed.
        Here are some examples:
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
    
    'constraint_clarify':
        'I did not quite understand. Please clarify your current %s at the quality level of 0.\n',

    'constraint_not_found':
        'I could not find the %s in your message. Please provide it again.\n',

    'constraint_confirm':
        'Confirming: Is %s the correct %s?\n'
        'If it is correct, please ONLY return %s again in the chat.\n'
        'Otherwise return your current %s at the quality level of 0.\n',

    'constraint_persist_final_buyer':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Retail Prices to Consumers has values between 8 and 10. Thus, I will assume your actual value is 10. \n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag?'
        'Please return the current proposal in square brackets. For example [Wholesale Price, Quality].',

    'constraint_persist_final_supplier':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Production Cost has values between 1 and 3. Thus, I will assume your actual value is 1. \n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag?'
        'Please return the current proposal in square brackets. For example [Wholesale Price, Quality].',
    
    'constraint_final_buyer':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag? '
        'Please return the current proposal in square brackets. For example [Wholesale Price, Quality].',
    
    'constraint_final_supplier':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag? '
        'Please return the current proposal in square brackets. For example [Wholesale Price, Quality].',

    'accept_offer': 
        'I am pleased to accept your offer! Thank you for investing time and effort in these negotiations! I look forward to a successful partnership.',
    
    'they_accept_offer': 
        'Thank you for negotiating with us! We are looking forward to a successful partnership.',
    
    'respond_to_offer':
        'I appreciate your offer, but I am looking for a different combination of Price and Quality. How about Wholesale %s? '
        'If you are not satisfied with this offer, please return your counter proposal in square brackets. For example [Wholesale Price, Quality].',

    'respond_to_non_offer':
        'I am sorry, but your offer is not valid. This is either because I did not recognize it, proposed terms were out of bounds or price or quality were not integers. How about Wholesale %s?'
        ' If you are not satisfied with this offer, please return  your counter proposal in square brackets. For example [Wholesale Price, Quality]. Only put integers in the squared brackets. '
}

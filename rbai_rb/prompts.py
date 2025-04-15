import os  # For file path operations
from typing import Dict  # For type annotations

from shared import rnd_param
from rbai_rb.rbai_storage import rbai_storage

# Get the absolute path of the rbai_rb directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

def from_file(base_path, file_path):
    full_path = os.path.join(BASE_DIR, base_path, file_path)  
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, 'r') as f:
        return f.read()




# Generates a system prompt based on the bot's role and constraints
# Constructs a message using predefined phrases and calculated constraint ranges
def system_final_prompt():
    bot_role = rnd_param.role
    if bot_role == 'supplier':
        production_cost = rbai_storage.main_bot_cons
        retail_price = rbai_storage.other_constraint
    else: 
        production_cost = rbai_storage.other_constraint
        retail_price = rbai_storage.main_bot_cons

    before_constraint = PROMPTS[bot_role]['before_constraint']
    bot_constraint = \
        production_cost if bot_role == "supplier" else retail_price
    after_constraint = PROMPTS[bot_role]['after_constraint_before_price']

    
    f = 1 - 2 * (bot_role == "buyer")
    constraints = str([f * (i - bot_constraint) for i in rnd_param.PRICE_RANGE])
    after_price = PROMPTS[bot_role]['after_price']

    return (before_constraint +
            f"{bot_constraint}€" +
            after_constraint +
            constraints +
            after_price)



# The functions below dynamically generate promts for different negotiations situations
# empty_offer_prompt: Handles cases where no valid offer was received.
def empty_offer_prompt(bot2_message: str,
                       offers_pareto_efficient: str,
                       interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_offer'] +
            bot2_message + ' ' +
            prompts['non_profitable_offer_or_deal'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)


# offer_without_quality_prompt: Handles cases where quality is missing in the bot2 offer
def offer_without_quality_prompt(bot2_message: str,
                                 offers_pareto_efficient: str,
                                 interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_quality'] +
            bot2_message + ' ' +
            prompts['non_quality_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)


# offer_without_price_prompt: Handles cases where price is missing in the bot2 offer
def offer_without_price_prompt(bot2_message: str,
                               offers_pareto_efficient: str,
                               interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_price'] +
            bot2_message + ' ' +
            prompts['non_price_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)



# not_profitable_prompt: Responds when the bot2 offer isn't profitable
def not_profitable_prompt(bot2_message: str,
                          offers_pareto_efficient: str,
                          interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_2nd'] +
            bot2_message + ' ' +
            prompts['non_profitable_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)


# offer_invalid: Handles invalid offers
def offer_invalid(bot2_message: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_invalid_offer'] +
            bot2_message + ' ' +
            prompts['invalid_offer_reminder'])


# Dynamically loads prompts from text files based on the bot’s role (buyer or supplier).
def role_prompts(base: str) -> Dict[str, str]:
    return {
        'before_constraint': from_file(base, 'system/before_constraint.txt'),
        'after_constraint_before_price': from_file(
            base, 'system/after_constraint_before_price.txt'),
        'after_price': from_file(base, 'system/after_price.txt'),
        'initial': from_file(base, 'intro_user.txt'),

        'follow_up_prompt_2nd': from_file(base, 'follow_up_user_message.txt'),
        'follow_up_prompt_without_offer': from_file(
            base, 'follow_up_user_message_without_offer.txt'),
        'follow_up_prompt_without_price': from_file(
            base, 'follow_up_user_message_without_price.txt'),
        'follow_up_prompt_without_quality': from_file(
            base, 'follow_up_user_message_without_quality.txt'),
        'non_profitable_offer': from_file(
            base, 'non_profitable_Send_Pareto_Efficient_Offer.txt'),
        'non_profitable_offer_or_deal': from_file(
            base, 'Send_Pareto_Efficient_or_Instructions.txt'),
        'follow_up_conversation': from_file(
            base, 'follow_up_conversation_history.txt'),
        'non_quality_offer': from_file(
            base, 'Not_Quality_Send_Pareto_Efficient_Offer.txt'),
        'follow_up_invalid_offer': from_file(
            base, 'follow_up_user_message_invalid_offer.txt'),
        'invalid_offer_reminder': from_file(
            base, 'invalid_offer_reminder.txt'),
        'non_price_offer': from_file(
            base, 'Not_Price_Send_Pareto_Efficient_Offer.txt'),
    }

# static promts: first message, closing message
PROMPTS = {
    'first_message_PC': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?",
    'first_message_RP': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price to Consumer?",
    'offer_string': f"Price of %s€ and quality of %s",
    'constraints': 'Here is the negotiator message you need to read: ',
    'context_constraint': {
        'buyer': 'Base Production Cost (PC)',
        'supplier': 'Base Retail Price to Consumer (RP)',
    },
    'constraint_clarify':
        'I did not quite understand. Please clarify your current %s at the quality level of 0.\n',
        
    'constraint_confirm':
        'Confirming: Is %s the correct %s?\n'
        'If it is correct, please ONLY return %s again in the chat.\n'
        'Otherwise return your current %s at the quality level of 0.\n',
                
    'constraint_offer':
        'I am not ready to respond to your offer yet. '
        'Please clarify your current %s at the quality level of 0 (in the chat bellow).',
    
    'constraint_persist_final_buyer':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Retail Prices to Consumers has values between 8 and 10. Thus, I will assume your actual value is 10. \n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag?',
    'constraint_persist_final_supplier':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Production Cost has values between 1 and 3. Thus, I will assume your actual value is 1. \n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag?',
    'constraint_final_buyer':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag?',
    'constraint_final_supplier':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag?',    
    
    'understanding_offer': 
        'Here is the negotiator message you need to read: '
        '%s'
        'Only return single instance of [], for the numerical wholesale price and quality. In your response, you can use sqare brackets [] ONCE.',

    'accept_from_chat': 
        'Accept the offer sent by your negotiation counterpart '
        'because the price and quality terms are favourable, '
        'thank your counterpart for their understanding.'
        '(Maximum 30 words and one paragraph). '
        'In your response repeat the terms of that you have accepted from the last message from your counterpart.'
        'Here is the last message from your counterpart: ',

    
    'evaluate_situation': 
        """'Your task is to determine whether the negotiation conversation has reached a conclusion or is still ongoing.
        The conversation history is formatted as a structured list with roles:
        - Messages sent by you (the assistant) have the role **"assistant"**, and their content is stored in the "content" field.
        - Messages from your counterpart (the user) have the role **"user"**, and their content is also stored in the "content" field.
        
        Here are some examples:
        Message: {'role': 'assistant', 'content': "I'm afraid our revised proposal still has an invalid offer. I'll suggest a compromise: Wholesale price of 10€ and Quality level 4. Would you consider that?"}, {'role': 'user', 'content': "That's an interesting suggestion! A wholesale price of 10€ is actually matching my Base Retail Price to Consumer, which is fixed at 10€.\n\nConsidering the quality level of 4, which aligns with my initial goal, I'm willing to accept your compromise proposal. A wholesale price of 10€ and a quality level of 4 would result in a total payoff that's acceptable to me.\n\nSo, yes, I'd be happy to accept your revised offer!"}
        Output: DEAL
        
        Message: {'role': 'assistant', 'content': "I'm willing to consider a wholesale price of 6€ paired with a quality level of 1."}, {'role': 'user', 'content': "A slight increase in quality for a slightly higher wholesale price! I think that's a great direction to explore. Given our payoff tables, I believe we can reach an agreement that benefits both parties. I'm willing to accept your proposal: a wholesale price of 6€ paired with a quality level of 1"}
        Output: DEAL

        Message: {'role': 'assistant', 'content': "I've reflected on our conversation and considered my negotiation rules. Since I aim to negotiate the best possible agreement for myself as the Supplier, I want a low quality and high wholesale price. I'll respond by choosing a combination that matches or builds upon the wholesale price mentioned in your opening offer - which was 5€. Therefore, I choose Price of 8€ and Quality of 2."}, {'role': 'user', 'content': "You're aiming to negotiate a high-quality agreement for yourself as the Supplier! By building upon my opening offer's Wholesale price of 5€, you've chosen an interesting combination.\n\nI'll analyze this proposal: a 10kg bag of wood pellets with Quality level 2 at Wholesale price 8€. Considering my payoffs table, I can see that this combination provides a decent payoff for me as the Buyer.\n\nHowever, I'm not willing to accept an agreement that yields a total payoff less than zero, which is according to our negotiation rules. Since my current total payoff would be lower than zero if I accepted your proposal, I'll make a counteroffer to maintain a positive payoff.\n\nI'll propose: 10kg bag of wood pellets with Quality level 1 at Wholesale price 7€. This combination provides a slightly better total payoff for me compared to your original offer.\n\nYour turn!"} 
        Output: Continue
        
        Below is the full conversation history so far:
        "%s" \n

        You must return exactly **ONE word** as your response:
        - If you determine that a final agreement has been reached (either you agree with counterparts offer or they agree with your offer), return **"DEAL"**.
        - If the negotiation is still ongoing, return **"CONTINUE"**.
        IMPORTANT: Do **NOT** provide any additional words, explanations, or context—only return "DEAL" or "CONTINUE".""",

    'end_negotiation': 
        'It seems that the negotiation has ended. '
        'Thank you for reaching a deal and for your time. '
        'Here is the last message received from the negotiator: "%s".',

    'return_same_message': 
        'Summarize the following conclusion while preserving its core meaning. '
        'Ensure clarity and conciseness but do not add new information. '
        'Keep the key message intact. \n'
        '"%s" \n'
        'Now, relay (return) this summary to the other negotiator. In your answer DO NOT use quotation marks.',

    'give_own_const':
        ' Please return your %s.'
        'Your assigned constraint can be found in the initial system message within the conversation history, specifically in the "content" field. '
        'Your response must exactly match the following format: "My %s is €%s." '
        'Do not include any additional text.',


    'supplier': role_prompts('./prompts/supplier/'),
    'buyer': role_prompts('./prompts/buyer/'),
}


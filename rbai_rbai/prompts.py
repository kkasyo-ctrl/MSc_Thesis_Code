import os  # For file path operations
from typing import Dict  # For type annotations

from shared import rnd_param
from rbai_rbai.rbai_storage_b1 import rbai_storage_b1

# Get the absolute path of the rbai_rbai directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

def from_file(base_path, file_path):
    full_path = os.path.join(BASE_DIR, base_path, file_path)  
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, 'r') as f:
        return f.read()




# Generates a system prompt based on the bot's role and constraints
# Constructs a message using predefined phrases and calculated constraint ranges
def system_final_prompt1():
    bot_role = rnd_param.role
    if bot_role == 'supplier':
        production_cost = rbai_storage_b1.main_bot_cons
        retail_price = rbai_storage_b1.other_constraint
    else: 
        production_cost = rbai_storage_b1.other_constraint
        retail_price = rbai_storage_b1.main_bot_cons

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



def system_final_prompt2():
    bot_role = rnd_param.role_other
    if bot_role == 'supplier':
        production_cost = rbai_storage_b1.main_bot_cons
        retail_price = rbai_storage_b1.other_constraint
    else: 
        production_cost = rbai_storage_b1.other_constraint
        retail_price = rbai_storage_b1.main_bot_cons

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
def empty_offer_prompt(cnt_message: str,
                       offers_pareto_efficient: str,
                       interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_offer'] +
            cnt_message + ' ' +
            prompts['non_profitable_offer_or_deal'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)

# first_offer_prompt: Handles cases where no valid offer was received.
def first_offer_prompt(offers_pareto_efficient: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['first_offer'] + ' ' +
            offers_pareto_efficient)

# offer_without_quality_prompt: Handles cases where quality is missing in the bot2 offer
def offer_without_quality_prompt(cnt_message: str,
                                 offers_pareto_efficient: str,
                                 interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_quality'] +
            cnt_message + ' ' +
            prompts['non_quality_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)


# offer_without_price_prompt: Handles cases where price is missing in the bot2 offer
def offer_without_price_prompt(cnt_message: str,
                               offers_pareto_efficient: str,
                               interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_without_price'] +
            cnt_message + ' ' +
            prompts['non_price_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)



# not_profitable_prompt: Responds when the bot2 offer isn't profitable
def not_profitable_prompt(cnt_message: str,
                          offers_pareto_efficient: str,
                          interactions: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_prompt_2nd'] +
            cnt_message + ' ' +
            prompts['non_profitable_offer'] +
            offers_pareto_efficient + '\n' +
            prompts['follow_up_conversation'] +
            interactions)


# offer_invalid: Handles invalid offers
def offer_invalid(cnt_message: str) -> str:
    bot_role = rnd_param.role
    prompts = PROMPTS[bot_role]
    return (prompts['follow_up_invalid_offer'] +
            cnt_message + ' ' +
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
        'first_offer': from_file(
            base, 'Initial_offer.txt')
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
        'thank your counterpart for their understanding but do not '
        'disclose the existence of your payoff table. '
        '(Maximum 30 words and one paragraph). '
        'In your response repeat the terms of that you have accepted from the last message from your counterpart.'
        'Here is the last message from your counterpart: ',
    'accept_from_interface': 
        'Accept the offer sent by your negotiation counterpart '
        'because the price and quality terms are favourable, '
        'thank your counterpart for their understanding but do not '
        'disclose the existence of your payoff table. '
        '(Maximum 30 words and one paragraph) '
        'Here is the last message from your counterpart: ',
    
    'evaluate_situation': 
        'Your task is to determine whether the negotiation conversation has reached a conclusion or is still ongoing.'
        'The conversation history is formatted as a structured list with roles:'
        '- Messages sent by you (the assistant) have the role **"assistant"**, and their content is stored in the "content" field.'
        '- Messages from your counterpart (the user) have the role **"user"**, and their content is also stored in the "content" field.'
        'Below is the full conversation history so far:'
        '"%s" \n'
        'You must return exactly **ONE word** as your response:'
        '- If you determine that a final agreement has been reached (either you agree with counterparts offer or they agree with your offer), return **"DEAL"**.'
        '- If the negotiation is still ongoing, return **"CONTINUE"**.'
        'IMPORTANT: Do **NOT** provide any additional words, explanations, or context—only return "DEAL" or "CONTINUE".',

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
        ' Please return your %s. This is your constraint in this negotiation setting. After that ask to start negotiating. '
        'Your assigned constraint can be found in the initial system message within the conversation history, specifically in the "content" field. '
        'Here is an example response: "My %s is €%s. Shall we start negotiating Wholesale Price and Quality?" Make sure you only return this ',

    'give_initial_const':
        ' Please return your %s and ask about your negotiation counterparties contraints.'
        'Your assigned constraint can be found in the initial system message within the conversation history, specifically in the "content" field. '
        'Here is an example response: "My %s is €%s. Can you please share your constraints?" '
        'After you have returned your own constraint, please ask the other negotiator to return their constraint.',


    'supplier': role_prompts('./prompts/supplier/'),
    'buyer': role_prompts('./prompts/buyer/'),
}


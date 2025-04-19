import re
from rbai_rb.rb_storage import rb_storage
from rbai_rb.message_storage import MESSAGES
from rbai_rb.offer_rb import Offer
from rbai_rb.generate_responses import propose_offer
import time

# extract bot constraint - seems to work
def extract_constraint(text):
    if rb_storage.bot1_role == "buyer":
        key_phrases = r'(base production cost|base retail price to consumer|production cost|selling price to customer|cost of production|manufacturing cost|production expense|unit production cost|supplier cost)'
    else:
        key_phrases = r'(base retail price|retail price|base selling price|base retail selling price|current retail price|selling price to customer|consumer price|end-user price|list price|final sale price|market price|point of sale price)'
    
    pattern = r'[^.]*\b' + key_phrases + r'\b[^.]*\.'
    rel_sentence = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    print(pattern)
    if rel_sentence:
        sentence = rel_sentence.group().strip()
        print("Extracted sentence:")
        print(sentence)
    else:
        print("No sentence containing the specified phrases was found.")
        return None

    pat = r'(?:(?:[\€\u20AC]|EUR)\s*\d+(?:[,.]\d+)?|\d+(?:[,.]\d+)?\s*(?:[\€\u20AC]|EUR|euros?))'
    constraint = re.search(pat, sentence, re.IGNORECASE)
    context_constraint = MESSAGES['context_constraint'][rb_storage.bot1_role]

    if constraint:
        cost_str = constraint.group(0)
        for token in ['€', '\u20AC', 'EUR', 'euro', 'euros']:
            cost_str = cost_str.replace(token, '')
        cost_str = cost_str.strip()
        cost_str = re.sub(r'[^\d\.]', '', cost_str)
        return float(cost_str) if '.' in cost_str else int(cost_str)
    else:
        return MESSAGES['constraint_not_found'] % context_constraint



# add message to the extracted constraint
def augment_message(message):
    output = extract_constraint(message)
    context_constraint = MESSAGES['context_constraint'][rb_storage.bot1_role] 
    check_const = False

    if output != MESSAGES['constraint_not_found'] % context_constraint:
        if analyze_constraint(output):
            rb_storage.bot2_constraint = int(output)
            if check_const:        
                params = (output, context_constraint) * 2
                message = MESSAGES['constraint_confirm'] % params
            else:
                message = propose_offer()
        else:
            message = MESSAGES['constraint_clarify'] % context_constraint

    else:
        message = output
        
    return message

# check if the constraint is in range    
def analyze_constraint(int_const):
    if int_const is None:
        return False  
    constraint_user = int(int_const)
    bot1_role = rb_storage.bot2_role 
    if bot1_role == 'supplier':
        return 1 <= constraint_user <= 3
    else:
        return 8 <= constraint_user <= 10


# store the final constraint
def constraint_final(inp_msg):
 
    if isinstance(inp_msg, str):
        if not inp_msg.isdigit():
            constraint_user = extract_constraint(inp_msg)
        else:
            constraint_user = inp_msg
    else:
        constraint_user = inp_msg

    message = final_constraint = None
    if constraint_user is not None:
        if rb_storage.bot1_role == 'supplier':
            if analyze_constraint(constraint_user):
                message = MESSAGES['constraint_final_buyer']
                final_constraint = constraint_user
        
        else:
            if analyze_constraint(constraint_user):
                message = MESSAGES['constraint_final_supplier']
                final_constraint = constraint_user
    if message is None or final_constraint is None:
        if rb_storage.bot1_role == 'supplier':
            message = MESSAGES['constraint_persist_final_buyer']
        elif rb_storage.bot1_role == 'buyer':
            message = MESSAGES['constraint_persist_final_suppier']
        final_constraint = constant_draw_constraint()


    rb_storage.bot2_constraint = int(final_constraint)
    return message

# make up a constraint
def constant_draw_constraint() -> int:
    bot1_role = rb_storage.bot2_role  
    if bot1_role == 'supplier':
        return 1  
    else:
        return 10 


# interpret offer
def interpret_offer(text):
    print("interpret offer")
    idx = int(time.time())
    price_pattern = r'wholesale price.*?€\s?(\d+(?:\.\d+)?)'
    price_match = re.search(price_pattern, text, re.IGNORECASE)
    
    if not price_match:
        price_pattern = r'€\s?(\d+(?:\.\d+)?)'
        price_match = re.search(price_pattern, text)
    
    price = float(price_match.group(1)) if price_match else None

    quality_pattern = r'quality(?:\s*level)?\D*(\d+)'
    quality_match = re.search(quality_pattern, text, re.IGNORECASE)
    quality = int(quality_match.group(1)) if quality_match else None

    return Offer(idx=idx, from_chat=True, price=price, quality=quality)



# accept offer
def check_offer_acceptance(inp_msg: str) -> str:
    if isinstance(inp_msg, str):
        lower_msg = inp_msg.lower()
        # List of keywords that suggest acceptance
        acceptance_keywords = ['deal', 'agreed', 'accepted', 
                               'confirm', 'confirmed', 'sounds good', 
                               "let's do it", "i'm in", "it's a deal", 
                               'approved']
        if any(keyword in lower_msg for keyword in acceptance_keywords):
            rb_storage.end_convo = True
            return MESSAGES['they_accept_offer']
    return None

# Example usage:

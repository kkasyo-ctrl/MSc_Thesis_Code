import re
from rb_llm.storage import rb_storage
from rb_llm.message_storage import MESSAGES
from rb_llm.offer import Offer
import time
from rb_llm.chat import _chat_to_ai
from shared import rnd_param
from typing import Optional 

# extract bot constraint - seems to work
def extract_constraint(text):
    if rb_storage.bot1_role == "buyer":
        key_phrases = r'(base production cost|production cost|cost of production|manufacturing cost|production expense|unit production cost|supplier cost)'
    else:
        key_phrases = r'(base retail price|retail price|base selling price|base retail selling price|current retail price|selling price to customer|consumer price|end-user price|list price|final sale price|market price|point of sale price)'
    
    pattern = r'[^.]*\b' + key_phrases + r'\b[^.]*\.'
    rel_sentence = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
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
    if output != MESSAGES['constraint_not_found'] % context_constraint:
        if analyze_constraint(output):
            params = (output, context_constraint) * 2
            message = MESSAGES['constraint_confirm'] % params
        else:
            message = MESSAGES['constraint_clarify'] % context_constraint

    else:
        message = output
        
    return message


# check if the constraint is in range    
def analyze_constraint(int_const):
    if isinstance(int_const, int):
        constraint_user = int_const
    elif isinstance(int_const, str) and int_const.isdigit():
        constraint_user = int(int_const)
    else:
        return None
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
            message = MESSAGES['constraint_persist_final_supplier']
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
    def get_int(value: str) -> Optional[int]:
        """Extract integer or average a range like '6-7'."""
        try:
            if '-' in value and all(part.strip().isdigit() for part in value.split('-')):
                parts = value.split('-')
                return round(sum(float(part) for part in parts) / len(parts))
            return round(float("".join(char for char in value if char.isdigit() or char == '-')))
        except ValueError:
            return None

    text = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')

    idx = int(time.time())
    price = quality = None

    pattern_offer_currency = re.compile(r'\[\s*(€|\$)?\s*(-?\d+)\s*,\s*(\d+)\s*\]')
    match = pattern_offer_currency.search(text)

    if match:
        price_str, quality_str = match.group(2), match.group(3)
        price, quality = get_int(price_str), get_int(quality_str)

    if price is None or quality is None:
        pattern_offer_currency_after = re.compile(r'\[\s*(-?\d+)\s*(€|\$)?\s*,\s*(\d+)\s*(€|\$)?\s*\]')
        match_after = pattern_offer_currency_after.search(text)

        if match_after:
            price_str, quality_str = match_after.group(1), match_after.group(3)
            price, quality = get_int(price_str), get_int(quality_str)

    if price is None or quality is None:
        pattern_offer_no_currency = re.compile(r'\[\s*(-?\d+)\s*,\s*(\d+)\s*\]')
        match_fallback = pattern_offer_no_currency.search(text)

        if match_fallback:
            price_str, quality_str = match_fallback.group(1), match_fallback.group(2)
            price, quality = get_int(price_str), get_int(quality_str)

    return Offer(idx=idx, from_chat=True, price=price, quality=quality, offer_by=rb_storage.bot2_role)



# accept offer
def check_offer_acceptance(inp_msg: str) -> str:
    if isinstance(inp_msg, str):
        lower_msg = inp_msg.lower()
        acceptance_keywords = ['deal', 'agreed', 'accepted', 
                               'confirm', 'confirmed', 'sounds good', 
                               "let's do it", "i'm in", "it's a deal", 
                               'approved']
        not_acceptance = ["i'll counteroffer", "i'll counter-offer", "i'll counter offer", "will counter offer"
                          "i'll make a counteroffer", "i'll make a counter-offer", "i'll make a counter offer",
                          "make counter proposal", "not yet ready", "let's discuss further", "not agree", 
                          "don't have deal", "can we adjust" , "can we do", "can we agree"]

        if any(keyword in lower_msg for keyword in acceptance_keywords) and not any(phrase in lower_msg for phrase in not_acceptance):
            recent_messages = "\n".join(msg["content"] for msg in rb_storage.interaction_list_bot1[-4:])
            check = [{"role": "user", "content": MESSAGES['evalutate_conversation'] % recent_messages}]

            llm_check = _chat_to_ai(check, mod_used='llama3', temperature=0.1)
            if llm_check['content'].strip() == "DEAL":
                rb_storage.end_convo = True
                return MESSAGES['they_accept_offer']

            else:
                return None
    return None


# interpret own offer
def own_offer(text):
    idx = int(time.time())
    pattern = r'Price of\s*(\d+)[€]?\s*and\s*quality of\s*(\d+)'
    
    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        price, quality = map(int, matches[-1])
    else:
        return None  
    
    return Offer(idx=idx, from_chat=True, price=price, quality=quality, offer_by=rb_storage.bot1_role)
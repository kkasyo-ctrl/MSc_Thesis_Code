#### Logic
from rbai_rbai.prompts import PROMPTS, system_final_prompt2
from rbai_rbai.chat import _chat_to_ai
from shared import rnd_param
from rbai_rbai.rbai_storage_b2 import rbai_storage_b2
from rbai_rbai.rbai_storage_b2 import Offer
from typing import Any, Dict, Optional 
import time
from rbai_rbai import pareto_rbai_b2
import re


# extracts the constraint of counterpart from msg with external LLM
def extract_constraint(text):
    if rbai_storage_b2.bot2_role == "buyer":
        key_phrases = r'(base production cost|production cost|selling price to customer|cost of production|manufacturing cost|production expense|unit production cost|supplier cost)'
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

    integers = re.findall(r'\b\d+\b', sentence)

    if integers:
        return int(integers[0])
    else:
        context_constraint = PROMPTS['context_constraint'][rbai_storage_b2.bot1_role]
        return PROMPTS['constraint_clarify'] % context_constraint
   

# checks whether the constraint is within valid bounds
def constraint_in_range(constraint_bot2) -> bool:
    if constraint_bot2 is None:
        return False  

    constraint_bot2 = int(constraint_bot2)
    bot1_role = rnd_param.role  
    if bot1_role == 'supplier':  
        return 1 <= constraint_bot2 <= 3
    else:
        return 8 <= constraint_bot2 <= 10

# if the counterpart has not provided a valud constraint, the bot will assume the worst value
def constant_draw_constraint() -> int:
    bot1_role = rnd_param.role_other  
    if bot1_role == 'supplier':
        return 10  
    else:
        return 1 


# calculate profits
def add_profits(offer: Offer):
    offer.profits(rnd_param.role_other, rbai_storage_b2.other_constraint, rbai_storage_b2.main_bot_cons)


# extract price and quality values from the message
def interpret_offer(message: str, offer_by) -> Optional[Offer]:
    def get_int(value: str) -> Optional[int]:
        """Extracts an integer or processes a range like '6-7'."""
        try:
            return round(float("".join(char for char in value if char.isdigit() or char == '-')))
        except ValueError:
            return None
    
    idx = int(time.time())

    conversation_history = [{'role': 'user', 'content': PROMPTS['understanding_offer'] + message}]

    model_used = 'llm_reader'
    ai_response = _chat_to_ai(conversation_history, model_used, temperature=0.1)
    llm_output = ai_response['content']
        
    price = quality = None
    match_list = list(rnd_param.PATTERN_OFFER.finditer(llm_output))
    extracted_values = []  
    for match in match_list:
        parts = [part.replace('<', '').replace('>', '').strip() for part in match.group(0).split(',')]
        ints = [get_int(part.replace('€', '').replace('[', '').replace(']', '')) for part in parts]
        extracted_values.extend(ints)

    print(f'Extracted values: {extracted_values}')
        
    if len(extracted_values) == 1:
        price = quality = None
    elif len(extracted_values) == 2:
        price, quality = extracted_values
    elif len(extracted_values) == 3:
        if extracted_values[0] is not None and extracted_values[2] is not None:
            price, quality = extracted_values[0], extracted_values[2]
        elif extracted_values[1:] == [None, None] and extracted_values[0] is not None:
            price = extracted_values[0]
            quality = None
        elif extracted_values[:2] == [None, None] and extracted_values[2] is not None:
            quality = extracted_values[2]
            price = None
        elif extracted_values == [None, None, None]:
            price = None
            quality = None
        else:
            price = quality = None
    else:
        price = quality = None


    file_name = "C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/rbai_rbai/debug/interpret.csv"
    cleaned = llm_output.replace("\n", " ### ")
    with open(file_name, "a") as f:
        f.write(f"{message};{cleaned};{price};{quality}\n")
    
    return Offer(idx=idx, from_chat=True, price=price, quality=quality, offer_by=offer_by)

# call LLM for a response prompt
def get_llm_response(message: str):
    print("get_llm_response")     
    
    system_prompt = system_final_prompt2()
    conversation_history = [{"role": "system", "content": system_prompt},  
                            {"role": "user", "content": message}]
    
    model_used = 'rb'
    ai_response = _chat_to_ai(conversation_history,  model_used, temperature=0.1)


    llm_output = ai_response['content']
    return llm_output


# get pareto efficient offers
def get_greediness(constraint_bot2: int, constraint_bot: int) -> int:
    if constraint_bot2 not in (0, None):
        return pareto_rbai_b2.pareto_efficient_offer(constraint_bot2, constraint_bot,
                                        rnd_param.role_other, False)
    else:
        return 0



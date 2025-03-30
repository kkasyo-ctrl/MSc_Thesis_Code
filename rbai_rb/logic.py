#### Logic
from rbai_rb.prompts import PROMPTS, system_final_prompt
from rbai_rb.chat import _chat_to_ai
from shared import rnd_param
from rbai_rb.rbai_storage import rbai_storage
from rbai_rb.rbai_storage import Offer
from typing import Any, Dict, Optional 
import time
from rbai_rb import pareto_rbai


# extracts the constraint of counterpart from the message using the LLM
def interpret_constraints(message: str) -> Optional[int]:

    def log(result):
        file_name = \
            "C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/rbai_rb/debug/constraints.csv"
        cleaned_llm_output = llm_output.replace("\n", " ### ")
        with open(file_name, "a") as f:
            f.write(f"{message};{cleaned_llm_output};{result}\n") 

    conversation_history = [{'role': 'user', 'content': PROMPTS['constraints'] + message}]
    model_used = 'llm_constraint'
    ai_response = _chat_to_ai(conversation_history, model_used, temperature=0.1)
    
    # make it not print!!!
    llm_output = ai_response['content']
    
    match = rnd_param.PATTERN_CONSTRAINT.search(llm_output)
    if match is None:
            return None
        
    match_str = match.group(0).replace('[', '').replace(']', '')
    if match_str:
        log(round(float(match_str)))
        return round(float(match_str))
        

# checks whether the constraint is within valid bounds
def constraint_in_range(constraint_bot2) -> bool:
    if constraint_bot2 is None:
        return False  

    constraint_bot2 = int(constraint_bot2)
    bot1_role = rnd_param.role_other  
    if bot1_role == 'supplier':
    
    # Check if constraint is within production cost range
        return 1 <= constraint_bot2 <= 3
    else:
        # Check if constraint is within retail price range
        return 8 <= constraint_bot2 <= 10

# if the counterpart has not provided a valud constraint, the bot will assume the worst value
def constant_draw_constraint() -> int:
    bot1_role = rnd_param.role  
    if bot1_role == 'supplier':
        return 10  
    else:
        return 1 


# calculate profits for the bot and bot2 based on constraints
def add_profits(offer: Offer):
    offer.profits(rnd_param.role, rbai_storage.other_constraint, rbai_storage.main_bot_cons)



# process the LLM response to extract clean content - NOT SURE WHERE IT IS USED AS OF NOW
def extract_content(response: Dict[str, Any]) -> str:
    def remove_inner(string: str, start_char: str, end_char: str):
        while start_char in string and end_char in string:
            start_pos = string.find(start_char)
            end_pos = string.find(end_char, start_pos) + 1
            if 0 <= start_pos < end_pos:
                string = string[:start_pos] + string[end_pos:]
            else:
                break
        return string

    try:
        content: str = response.strip()
    except KeyError as _:
        print(f"\nUnexpected response format: {response}\n")
        return f"\nUnexpected response format: {response}\n"


    if content.count('"') > 1:
        start = content.find('"') + 1
        end = content.rfind('"')
        content = content[start:end]
    else:
        if content.lower().startswith("system:"):
            content = content[7:].strip()
        if content.lower().startswith("system,"):
            content = content[7:].strip()

    # Remove text within parentheses if no quotes are found
    content = remove_inner(content, '(', ')')
    # Remove content within square brackets
    content = remove_inner(content, '[', ']')

    # Remove text before "list_of_offers_to_choose_from"
    if 'list_of_offers_to_choose_from' in content:
        split_list = content.split('list_of_offers_to_choose_from:', 1)
        content = split_list[1].strip() if len(split_list) > 1 else content

    # Remove text before the first colon
    if ':' in content:
        split_list = content.split(':', 1)
        content = split_list[1].strip() if len(split_list) > 1 else content

    # Split the content at line breaks and take only the first part
    content = content.split('\n', 1)[0]

    return content.strip()


# extract price and quality values from the message and create an Offer object
def interpret_offer(message: str, offer_by) -> Optional[Offer]:
    def get_int(value: str) -> Optional[int]:
        """Extracts an integer or processes a range like '6-7'."""
        try:

            # Handle ranges like '6-7'
            if '-' in value and all(part.strip().isdigit() for part in value.split('-')):
                parts = value.split('-')
                return round(sum(float(part) for part in parts) / len(parts))

            # Handle single values
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


    file_name = "C:/Users/david/Desktop/MSc Thesis/MSc Code/github/MSc_Thesis_Code/rbai_rb/debug/interpret.csv"
    cleaned = llm_output.replace("\n", " ### ")
    with open(file_name, "a") as f:
        f.write(f"{message};{cleaned};{price};{quality}\n")
    
    return Offer(idx=idx, from_chat=True, price=price, quality=quality, offer_by=offer_by)

# call LLM for a response prompt
def get_llm_response(message: str):
    print("get_llm_response")    
    
    
    system_prompt = system_final_prompt()
    conversation_history = [{"role": "system", "content": system_prompt},  
                            {"role": "user", "content": message}]
    
    model_used = 'llama3'
    ai_response = _chat_to_ai(conversation_history,  model_used, temperature=0.1)


    llm_output = ai_response['content']
    return llm_output


# get pareto-efficient offers
def get_greediness(constraint_bot2: int, constraint_bot: int) -> int:
    if constraint_bot2 not in (0, None):
        return pareto_rbai.pareto_efficient_offer(constraint_bot2, constraint_bot,
                                        rnd_param.role, False)
    else:
        return 0



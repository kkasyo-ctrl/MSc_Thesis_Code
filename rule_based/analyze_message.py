import re
from shared import rnd_param
from rule_based.storage import rb_storage

# extract bot constraint - seems to work
def extract_constraint(text):
    if rb_storage.bot_role == "buyer":
        key_phrases = r'(base production cost|production cost|selling price to customer|cost of production|manufacturing cost|production expense|unit production cost|supplier cost)'
    else:
        key_phrases = r'(base retail price|retail price|current retail price|selling price to customer|consumer price|end-user price|list price|final sale price|market price|point of sale price)'
    
    pattern = r'[^.]*\b' + key_phrases + r'\b[^.]*\.'
    print("Regex pattern:", pattern)
    rel_sentence = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

    if rel_sentence:
        sentence = rel_sentence.group().strip()
        print("Extracted sentence:")
        print(sentence)
    else:
        print("No sentence containing the specified phrases was found.")
        return None

    pat = r'€\s*\d+(?:[,.]\d+)?'
    constraint = re.search(pat, sentence, re.IGNORECASE)
    
    if constraint:
        cost_str = constraint.group(0)
        int_const = float(cost_str.replace('€', '').strip()) if '.' in cost_str else int(cost_str.replace('€', '').strip())
    else:
        print("No price found in the extracted sentence.")
    
    if analyze_constraint(int_const):
        message = "Yes"
    else:
        message = "NO"
    
    return message

    
def analyze_constraint(int_const):
    if int_const is None:
        return False  

    constraint_user = int(int_const)
    bot1_role = rb_storage.other_role  
    if bot1_role == 'supplier':
        return 1 <= constraint_user <= 3
    else:
        return 8 <= constraint_user <= 10
            

# Example message text
message = """ My base production cost for producing wood pellets at quality 0 is €2."""

extract_constraint(message)


# Extracting the base production cost
base_cost = extract_constraint(message)
print("Base production cost:", base_cost)

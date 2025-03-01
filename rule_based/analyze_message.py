import re
from shared import rnd_param
from rule_based.storage import rb_instance
from rule_based.message_storage import MESSAGES

# extract bot constraint - seems to work
def extract_constraint(text):
    if rb_instance.bot1_role == "buyer":
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

    pat = r'[\€\u20AC]\s*\d+(?:[,.]\d+)?'  
    constraint = re.search(pat, sentence, re.IGNORECASE)
    
    if constraint:
        cost_str = constraint.group(0)
        int_const = float(cost_str.replace('€', '').strip()) if '.' in cost_str else int(cost_str.replace('€', '').strip())
    else:
        message = MESSAGES['constraint_not_found'] % context_constraint
    
    context_constraint = MESSAGES['context_constraint'][rb_instance.bot1_role]
    if analyze_constraint(int_const):
        params = (int_const, context_constraint) * 2
        message = MESSAGES['constraint_confirm'] % params
    else:
        message = MESSAGES['constraint_clarify'] % context_constraint

        
    return message

    
def analyze_constraint(int_const):
    if int_const is None:
        return False  
    print(int_const)
    constraint_user = int(int_const)
    bot1_role = rb_instance.bot2_role 
    if bot1_role == 'supplier':
        return 1 <= constraint_user <= 3
    else:
        return 8 <= constraint_user <= 10
            

# Example message text
message = """ My base retail selling price for the lowest quality wood pellets is €9 per kilogram. This gives us a baseline to work from.

Now, I'm interested in hearing about your company's needs and constraints before we dive into the wholesale price discussion. What are your expectations, and what do you hope to achieve from our negotiation?"""

extract_constraint(message)


# Extracting the base production cost
base_cost = extract_constraint(message)
print("Base production cost:", base_cost)

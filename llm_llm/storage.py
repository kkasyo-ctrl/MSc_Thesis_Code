# Role-based system storage
# import packages 
import sys
import os
from shared import rnd_param
import csv
import datetime

class llm_storage:
    bot1_role = rnd_param.role_other
    bot2_role = rnd_param.role
    interaction_list_bot1 = None
    interaction_list_bot2 = None
    agreed_price = None
    agreed_quality = None 
    bot1_const = rnd_param.other_constraint
    bot1_const = rnd_param.main_constraint
    profit_bot1 = None
    profit_bot2 = None



def extract_price_and_quality(string_data):
    if not (string_data.startswith('[') and string_data.endswith(']')):
        raise ValueError("Input must be enclosed in square brackets, e.g., '[10,9]'.")
    
    content = string_data[1:-1]
    parts = content.split(',')
    
    if len(parts) != 2:
        raise ValueError("Input must contain exactly two numbers separated by a comma.")
    
    try:
        price = int(parts[0].strip())
        quality = int(parts[1].strip())
    except ValueError:
        raise ValueError("Both price and quality must be valid integers.")
    
    return price, quality

def calculate_profits():
    price = rnd_param.main_constraint
    quality = rnd_param.other_constraint
    if llm_storage.bot1_role == "buyer":
        profit_bot1 = llm_storage.bot1_const - price + quality
        profit_bot2 = price - llm_storage.bot1_const - quality
        
    elif llm_storage.bot1_role == "supplier":
        profit_bot1 = price - llm_storage.bot1_const - quality
        profit_bot2 = price - llm_storage.bot1_const - quality
    
    llm_storage.profit_bot1 = profit_bot1
    llm_storage.profit_bot2 = profit_bot2


def saving_convo():
    save_path = os.path.join("rule_based", "output.csv")  # Ensure correct save location

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  # Use `;` as separator
        writer.writerow([datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), rnd_param.role, rnd_param.role_other, rnd_param.other_constraint, rnd_param.main_constraint,
                         llm_storage.agreed_price, llm_storage.agreed_quality, llm_storage.profit_bot1, llm_storage.profit_bot2, 
                         len(llm_storage.interaction_list_bot1) - 1,llm_storage.interaction_list_bot1])  



# storage of system variables
from typing import Optional
from rbai_llm.offer import Offer, OfferList 
from shared import rnd_param
import csv
import datetime
import os

# system storage
class Storage:
    main_bot_cons = rnd_param.main_constraint
    other_constraint = 'Unknown'
    bot2_message = None
    offer_bot2: Optional[Offer] = None
    offer_list: Optional[OfferList] = None
    interaction_list_bot2 = None
    interaction_list_bot1 = None
    offers_pareto_efficient = None
    end_convo = False


# update system - each time modify message is called this will be added. Hence the buyer price is: will be there like million times
def update_system(history):
    #hist = history[0]['content']
    #hist= history[0]['content'] + f" The buyer price is: {Storage.other_constraint}"
    return history



def saving_convo():
    save_path = os.path.join("rbai_llm", "output.csv")  # Ensure correct save location

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  # Use `;` as separator
        writer.writerow([datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), rnd_param.role, rnd_param.role_other, rnd_param.main_constraint, rnd_param.other_constraint, 
                         Storage.offer_list[-1].price, Storage.offer_list[-1].quality, Storage.main_bot_cons, Storage.other_constraint, 
                         Storage.offer_list[-1].profit_bot1, Storage.offer_list[-1].profit_bot2, len(Storage.offer_list), 
                         len(Storage.interaction_list_bot1) - 1,Storage.interaction_list_bot2, Storage.offer_list])  

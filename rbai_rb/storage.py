# Role-based system storage
# import packages 
import sys
import os
from shared import rnd_param
from rb_llm.offer import Offer, OfferList
from typing import Optional
import csv
import datetime

class rb_storage:
    bot1_role = rnd_param.role_other
    bot2_role = rnd_param.role
    bot1_constraint = rnd_param.other_constraint
    bot2_constraint = 'Unknown'
    bot2_message = None
    interaction_list_bot1 = None
    interaction_list_bot2 = None
    offer_user: Optional[Offer] = None
    offer_list: Optional[OfferList] = None
    offers_pareto_efficient = None
    end_convo = False




def saving_convo():
    save_path = os.path.join("rb_llm", "output.csv")  # Ensure correct save location

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  # Use `;` as separator
        writer.writerow([datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), rnd_param.role_other, rnd_param.other_constraint, rnd_param.main_constraint, 
                         rb_storage.offer_list[-1].price, rb_storage.offer_list[-1].quality, rb_storage.bot1_constraint, rb_storage.bot2_constraint, 
                         rb_storage.offer_list[-1].profit_bot, rb_storage.offer_list[-1].profit_user, len(rb_storage.offer_list), 
                         len(rb_storage.interaction_list_bot1) - 1,rb_storage.interaction_list_bot1, rb_storage.offer_list])  



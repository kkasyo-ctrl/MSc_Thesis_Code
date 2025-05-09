# Role-based system storage
# import packages 
import sys
import os
from shared import rnd_param
from rb_llm.offer import Offer, OfferList
from typing import Optional
import csv
import datetime

# storage class for rb
class rb_storage:
    bot1_role = rnd_param.role_other
    bot2_role = rnd_param.role
    bot1_constraint = rnd_param.other_constraint
    bot2_constraint = 'Unknown'
    bot2_message = None
    interaction_list_bot1 = None
    interaction_list_bot2 = None
    offer_bot1: Optional[Offer] = None
    offer_bot2: Optional[Offer] = None
    offer_list: Optional[OfferList] = None
    offers_pareto_efficient = None
    end_convo = False
    
    @classmethod
    def reset(cls):
        cls.bot1_role = rnd_param.role_other
        cls.bot2_role = rnd_param.role
        cls.bot1_constraint = rnd_param.other_constraint
        cls.bot2_constraint = 'Unknown'
        cls.bot2_message = None
        cls.interaction_list_bot1 = None
        cls.interaction_list_bot2 = None
        cls.offer_bot1 = None
        cls.offer_bot2 = None
        cls.offer_list = None
        cls.offers_pareto_efficient = None
        cls.end_convo = False



# save info
def saving_convo():
    save_path = os.path.join("rb_llm", "output.csv")  

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        last_offer = rb_storage.offer_list[-1] if rb_storage.offer_list else None

        if last_offer is None:
            writer.writerow([
                timestamp,
                rnd_param.role_other, rnd_param.role, rnd_param.other_constraint, rnd_param.main_constraint, "NO DEAL", "NO DEAL", rb_storage.bot1_constraint,
                rb_storage.bot2_constraint, "NO DEAL", "NO DEAL",  len(rb_storage.offer_list), len(rb_storage.interaction_list_bot1), rb_storage.interaction_list_bot1,
                rb_storage.offer_list ])
        else:
            writer.writerow([
                timestamp, rnd_param.role_other, rnd_param.role, rnd_param.other_constraint, rnd_param.main_constraint, last_offer.price, last_offer.quality,
                rb_storage.bot1_constraint, rb_storage.bot2_constraint, last_offer.profit_bot1, last_offer.profit_bot2, len(rb_storage.offer_list), 
                len(rb_storage.interaction_list_bot1), rb_storage.interaction_list_bot1, rb_storage.offer_list ])


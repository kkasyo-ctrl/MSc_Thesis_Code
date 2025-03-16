# storage of system variables
from typing import Optional
from rbai_rbai.offer_b1 import Offer, OfferList 
from shared import rnd_param
import csv
import datetime
import os
from rbai_rbai.rbai_storage_b2 import rbai_storage_b2

# system storage
class rbai_storage_b1:
    bot1_role = rnd_param.role
    bot2_role = rnd_param.role_other
    main_bot_cons = rnd_param.main_constraint
    other_constraint = 'Unknown'
    bot2_message = None
    offer_bot2: Optional[Offer] = None
    offer_list: Optional[OfferList] = None
    interaction_list_bot2 = None
    interaction_list_bot1 = None
    offers_pareto_efficient = None
    end_convo = False


def saving_convo():
    save_path = os.path.join("rbai_rbai", "output.csv")  # Ensure correct save location

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  # Use `;` as separator
        writer.writerow([datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), rnd_param.role, rnd_param.role_other, rnd_param.main_constraint, rnd_param.other_constraint, 
                         rbai_storage_b1.offer_list[-1].price, rbai_storage_b1.offer_list[-1].quality, rbai_storage_b1.main_bot_cons, rbai_storage_b1.other_constraint, 
                         rbai_storage_b2.other_constraint, rbai_storage_b2.main_bot_cons, rbai_storage_b1.offer_list[-1].profit_bot1, rbai_storage_b1.offer_list[-1].profit_bot2,
                         len(rbai_storage_b1.offer_list), len(rbai_storage_b1.interaction_list_bot1),rbai_storage_b1.interaction_list_bot1, rbai_storage_b1.offer_list])  

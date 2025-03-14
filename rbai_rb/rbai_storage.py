# storage of system variables
from typing import Optional
from rbai_rb.offer_rbai import Offer, OfferList 
from shared import rnd_param
import csv
import datetime
import os
from rbai_rb.rb_storage import rb_storage

# system storage
class rbai_storage:
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
    save_path = os.path.join("rbai_rb", "output.csv")  # Ensure correct save location

    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")  # Use `;` as separator
        writer.writerow([datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), rnd_param.role, rnd_param.role_other, rnd_param.main_constraint, rnd_param.other_constraint, 
                         rbai_storage.offer_list[-1].price, rbai_storage.offer_list[-1].quality, rbai_storage.main_bot_cons, rbai_storage.other_constraint, 
                         rb_storage.bot2_constraint,rb_storage.bot1_constraint, rbai_storage.offer_list[-1].profit_bot1, rbai_storage.offer_list[-1].profit_bot2,
                         len(rbai_storage.offer_list), len(rbai_storage.interaction_list_bot1),rbai_storage.interaction_list_bot1, rbai_storage.offer_list])  

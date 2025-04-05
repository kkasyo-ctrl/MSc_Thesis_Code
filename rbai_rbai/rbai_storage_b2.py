# storage of system variables
from typing import Optional
from rbai_rbai.offer_b2 import Offer, OfferList 
from shared import rnd_param
import csv
import datetime
import os

# system storage
class rbai_storage_b2:
    bot1_role = rnd_param.role
    bot2_role = rnd_param.role_other
    main_bot_cons = rnd_param.other_constraint
    other_constraint = 'Unknown'
    bot1_message = None
    offer_bot2: Optional[Offer] = None
    offer_list: Optional[OfferList] = None
    interaction_list_bot2 = None
    interaction_list_bot1 = None
    offers_pareto_efficient = None
    end_convo = False

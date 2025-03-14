# Role-based system storage
# import packages 
from shared import rnd_param
from rb_llm.offer import Offer, OfferList
from typing import Optional

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


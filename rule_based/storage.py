# Role-based system storage
# import packages 
import sys
import os
from shared import rnd_param


class rb_storage:
    bot_role = rnd_param.role_other
    other_role = rnd_param.role
    bot_constraint = rnd_param.other_constraint
    other_constraint = 'Unknown'
    user_message = None
    interaction_list_bot1 = None
    offers_pareto_efficient = None
    end_convo = False
    

# Role-based system storage
# import packages 
import sys
import os
from shared import rnd_param


class rb_storage:
    def __init__(self):
        self.bot1_role = rnd_param.role_other
        self.bot2_role = rnd_param.role
        self.bot_constraint = rnd_param.other_constraint
        self.other_constraint = 'Unknown'
        self.user_message = None
        self.interaction_list_bot1 = None
        self.offers_pareto_efficient = None
        self.end_convo = False


rb_instance = rb_storage()


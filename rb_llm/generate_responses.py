# generate responses to the counterparty
from rb_llm.storage import rb_storage
from rb_llm import pareto  
from rb_llm.offer import (Offer, OfferList, ACCEPT, OFFER_QUALITY, OFFER_PRICE,
                    NOT_OFFER, INVALID_OFFER, NOT_PROFITABLE)
from rb_llm.message_storage import MESSAGES 
import random
from rb_llm.analyze_message import own_offer

# return initial message 
def initial_message():
    if rb_storage.bot1_role == "buyer":
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?"
    else:
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price?"

    return message

# evaluate the current offer
def evaluate():
    print('evaluate')
 
    if rb_storage.offer_list is not None:
        for off in rb_storage.offer_list:
            add_profits(off)


    greedy = get_greediness(rb_storage.bot2_constraint,rb_storage.bot1_constraint)  
    print(f'greedy: {greedy}') 
    rb_storage.offers_pareto_efficient = pareto.pareto_efficient_string(
        rb_storage.bot2_constraint,rb_storage.bot1_constraint, rb_storage.bot1_role
    )
    print(f'offers_pareto_efficient: {rb_storage.offer_bot2}')
    evaluation = rb_storage.offer_bot2.evaluate(greedy)
    print(f'evaluation: {evaluation}')
    if evaluation == ACCEPT:
        return accept_offer()
    elif evaluation in (NOT_PROFITABLE, OFFER_PRICE, OFFER_QUALITY):
        return respond_to_offer()
    elif evaluation in (INVALID_OFFER, NOT_OFFER):
        return respond_to_non_offer()
    else:
        raise Exception

# calculate profits    
def add_profits(offer: Offer):
    offer.profits(rb_storage.bot1_role, rb_storage.bot2_constraint, rb_storage.bot1_constraint)
    print(offer.profits)

# calculate greediness (lazy workaround)
def get_greediness(constraint_user: int, constraint_bot: int) -> int:
    if constraint_user not in (0, None):
        return pareto.pareto_efficient_offer(constraint_user, constraint_bot,rb_storage.bot1_role, False)
    else:
        return 0
    
# acceot offer function
def accept_offer():
    print('accept')
    content = MESSAGES['accept_offer'] 
    rb_storage.end_convo = True

    return content

# offer pool
offer_pool = [] 

# return potential responses to offer (now with offer pool)
def respond_to_offer():
    global offer_pool

    if not offer_pool:
        offer_pool = pareto.pareto_efficient_string(rb_storage.bot2_constraint, rb_storage.bot1_constraint, rb_storage.bot1_role)
        random.shuffle(offer_pool)

    selected_offer = str(offer_pool.pop(0))
    print(f'remaining offers: {offer_pool}')
    rb_storage.offer_bot1 = own_offer(selected_offer)
    rb_storage.offer_list.append(rb_storage.offer_bot1)
    message = MESSAGES['respond_to_offer'] % selected_offer
    return message


# return potential responses to not offer (now with offer pool)
def respond_to_non_offer():
    global offer_pool
    
    if not offer_pool:
        offer_pool = pareto.pareto_efficient_string(rb_storage.bot2_constraint, rb_storage.bot1_constraint, rb_storage.bot1_role)
        random.shuffle(offer_pool)
        
    selected_offer = str(offer_pool.pop(0))
    print(f'remaining offers: {offer_pool}')
    rb_storage.offer_bot1 = own_offer(selected_offer)
    rb_storage.offer_list.append(rb_storage.offer_bot1)    
    message = MESSAGES['respond_to_non_offer'] % selected_offer
    return message


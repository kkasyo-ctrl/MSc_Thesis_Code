# generate responses to the counterparty
from rule_based.storage import rb_storage
from rule_based import pareto  
from rule_based.offer import (Offer, OfferList, ACCEPT, OFFER_QUALITY, OFFER_PRICE,
                    NOT_OFFER, INVALID_OFFER, NOT_PROFITABLE)
from rule_based.message_storage import MESSAGES 
import random

def initial_message():
    if rb_storage.bot1_role == "buyer":
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?"
    else:
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price?"

    return message

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
    print(f'offers_pareto_efficient: {rb_storage.offer_user}')
    evaluation = rb_storage.offer_user.evaluate(greedy)
    print(f'evaluation: {evaluation}')
    if evaluation == ACCEPT:
        return accept_offer()
    elif evaluation in (NOT_PROFITABLE, OFFER_PRICE, OFFER_QUALITY):
        return respond_to_offer()
    elif evaluation in (INVALID_OFFER, NOT_OFFER):
        return respond_to_non_offer()
    else:
        raise Exception
    
def add_profits(offer: Offer):
    offer.profits(rb_storage.bot1_role, rb_storage.bot2_constraint, rb_storage.bot1_constraint)
    print(offer.profits)


def get_greediness(constraint_user: int, constraint_bot: int) -> int:
    if constraint_user not in (0, None):
        return pareto.pareto_efficient_offer(constraint_user, constraint_bot,rb_storage.bot1_role, False)
    else:
        return 0
    

def accept_offer():
    print('accept')
    content = MESSAGES['accept_offer'] 
    rb_storage.end_convo = True
    accept_final_chat()

    return content


def accept_final_chat():
    bot_offer = Offer(
        idx=-1,
        price=rb_storage.offer_user.price,
        quality=rb_storage.offer_user.quality,
        test="accept_final_chat"
    )
    add_profits(bot_offer)
    rb_storage.offer_list.append(bot_offer)


def respond_to_offer():
    random_offer = pareto.pareto_efficient_string(rb_storage.bot2_constraint,rb_storage.bot1_constraint,rb_storage.bot1_role)
    print(f"random_offer: {random_offer}")
    offer_num = random.randint(0,len(random_offer)-1)
    random_offer = random_offer[offer_num]
    message = MESSAGES['respond_to_offer'] % random_offer
    return message


def respond_to_non_offer():
    random_offer = pareto.pareto_efficient_string(rb_storage.bot2_constraint,rb_storage.bot1_constraint,rb_storage.bot1_role)
    print(f"random_offer: {random_offer}")
    offer_num = random.randint(0,len(random_offer)-1)
    random_offer = random_offer[offer_num]
    message = MESSAGES['respond_to_non_offer'] % random_offer
    return message

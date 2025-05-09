# generate responses to the counterparty
from rbai_rb.rb_storage import rb_storage
from rbai_rb import pareto_rb   
from rbai_rb.offer_rb import (Offer, OfferList, ACCEPT, OFFER_QUALITY, OFFER_PRICE,
                    NOT_OFFER, INVALID_OFFER, NOT_PROFITABLE)
from rbai_rb.message_storage import MESSAGES 
import random

# initial message function
def initial_message():
    if rb_storage.bot1_role == "buyer":
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?"
    else:
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price?"

    return message

# evaluate the hybrid offer
def evaluate():
    print('evaluate')
 
    if rb_storage.offer_list is not None:
        for off in rb_storage.offer_list:
            add_profits(off)


    greedy = get_greediness(rb_storage.bot2_constraint,rb_storage.bot1_constraint)  
    print(f'greedy: {greedy}') 
    rb_storage.offers_pareto_efficient = pareto_rb.pareto_efficient_string(
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
    
# calculate the profits of the offer    
def add_profits(offer: Offer):
    offer.profits(rb_storage.bot1_role, rb_storage.bot2_constraint, rb_storage.bot1_constraint)
    print(offer.profits)

# get greediness (im lazy potentially change later)
def get_greediness(constraint_user: int, constraint_bot: int) -> int:
    if constraint_user not in (0, None):
        return pareto_rb.pareto_efficient_offer(constraint_user, constraint_bot,rb_storage.bot1_role, False)
    else:
        return 0
    
# accept the offer
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


# respond to unprofitable offer
def respond_to_offer():
    random_offer = pareto_rb.pareto_efficient_string(rb_storage.bot2_constraint,rb_storage.bot1_constraint,rb_storage.bot1_role)
    print(f"random_offer: {random_offer}")
    offer_num = random.randint(0,len(random_offer)-1)
    random_offer = random_offer[offer_num]
    message = MESSAGES['respond_to_offer'] % random_offer
    return message

# respond to non offer
def respond_to_non_offer():
    random_offer = pareto_rb.pareto_efficient_string(rb_storage.bot2_constraint,rb_storage.bot1_constraint,rb_storage.bot1_role)
    print(f"random_offer: {random_offer}")
    offer_num = random.randint(0,len(random_offer)-1)
    random_offer = random_offer[offer_num]
    message = MESSAGES['respond_to_non_offer'] % random_offer
    return message


# propose a counteroffer
def propose_offer():
    random_offer = pareto_rb.pareto_efficient_string(rb_storage.bot2_constraint,rb_storage.bot1_constraint,rb_storage.bot1_role)
    print(f"random_offer: {random_offer}")
    offer_num = random.randint(0,len(random_offer)-1)
    random_offer = random_offer[offer_num]
    message = MESSAGES['initial_offer'] % random_offer
    return message

# provide the hybrid with own constraint
def give_const(text):
    text_lower = text.lower()

    if rb_storage.bot1_role == "buyer":
        key_phrase = 'base retail price'
    else:
        key_phrase = 'base production cost'

    if "share" in text_lower and key_phrase in text_lower:
        if rb_storage.bot1_role == "buyer": 
            msg_ret = f"My base production cost is {rb_storage.bot1_constraint}. Can you share with me your base retail price?"
        else:
            msg_ret = f"My base retail price is {rb_storage.bot1_constraint}. Can you share with me your base production cost?"
    else:
        msg_ret = "Sorry, I did not quite understand that. Could you please clarify what do you mean?"
    
    return msg_ret

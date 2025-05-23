#### Activation 
# import packages
import os
from shared import rnd_param
from rbai_rbai import logic_b2
import json
import random
from typing import Any, List, Union
from rbai_rbai.rbai_storage_b2 import rbai_storage_b2
from rbai_rbai.rbai_storage_b1 import rbai_storage_b1
from rbai_rbai.pareto_rbai_b2 import pareto_efficient_string
from rbai_rbai.offer_b2 import (Offer, OfferList, ACCEPT, OFFER_QUALITY, OFFER_PRICE,
                    NOT_OFFER, INVALID_OFFER, NOT_PROFITABLE, FIRST_OFFER)
from rbai_rbai.prompts import (PROMPTS, not_profitable_prompt, empty_offer_prompt,
                      offer_without_price_prompt, offer_without_quality_prompt,
                      offer_invalid, first_offer_prompt)


# modify the bot message based on the execution count
execution_count = 0  
def modify_bot_message(message):
    global execution_count 
    if execution_count == 0: 
        execution_count += 1
        return provide_constraint()
    if execution_count == 1: 
        execution_count += 1
        return constraint_initial(message)
    else:  
        return interpretation(message)



# sends the initial message to the conterpart 
def initial():
    if rnd_param.role_other == "buyer":
        message = PROMPTS['first_message_PC']
    else:
        message = PROMPTS['first_message_RP']
    
    return message

# asks for constraints
def constraint_initial(message):

    constraint_bot2 = logic_b2.extract_constraint(message)
    context_constraint = PROMPTS['context_constraint'][rnd_param.role_other]
    rbai_storage_b2.other_constraint = int(constraint_bot2)

    if logic_b2.constraint_in_range(constraint_bot2):
        rbai_storage_b2.offers_pareto_efficient = pareto_efficient_string(rbai_storage_b2.other_constraint, rbai_storage_b2.main_bot_cons, rnd_param.role_other)
        rbai_storage_b2.bot1_message = message
        greedy = logic_b2.get_greediness(rbai_storage_b2.other_constraint, rnd_param.other_constraint)  
        content1 = get_respond_prompt(FIRST_OFFER)

        llm_offers = []
        last_offer = None
        evaluation = 'Not Proposed'
        while len(llm_offers) < 3 and evaluation != ACCEPT:
            response = logic_b2.get_llm_response(content1)
            last_offer = logic_b2.interpret_offer(response, offer_by=rnd_param.role_other)

            if last_offer.is_complete:
                logic_b2.add_profits(last_offer)
            else:
                last_offer.profit_bot1 = 0
                last_offer.profit_bot2 = 0

            llm_offers.append([last_offer.profit_bot1, response, last_offer])
            evaluation = last_offer.evaluate(greedy)
            print(f'Evalutation from the while loop: {evaluation}')
            print(f'Offer in offer.py: {OfferList}')
        
        return send_response(evaluation, last_offer, response, llm_offers)


    else:
        transformed_msg = PROMPTS['constraint_clarify'] % context_constraint

        return transformed_msg


# store the final constraint -> modified
def constraint_final(inp_msg):
    check_const = False 
    if check_const:
        print(f"constraint_final: {inp_msg}")
        if not inp_msg.isdigit():
            constraint_bot2 = logic_b2.interpret_constraints(inp_msg)
        else:
            constraint_bot2 = inp_msg

        message = final_constraint = None
        if constraint_bot2 is not None:
            if rnd_param.role_other == 'supplier':
                if logic_b2.constraint_in_range(constraint_bot2):
                    message = PROMPTS['constraint_final_buyer']
                    final_constraint = constraint_bot2
            
            else:
                if logic_b2.constraint_in_range(constraint_bot2):
                    message = PROMPTS['constraint_final_supplier']
                    final_constraint = constraint_bot2
        if message is None or final_constraint is None:
            if rnd_param.role_other == 'supplier':
                message = PROMPTS['constraint_persist_final_buyer']
            elif rnd_param.role_other == 'buyer':
                message = PROMPTS['constraint_persist_final_supplier']
            
            final_constraint = logic_b2.constant_draw_constraint()


        rbai_storage_b2.other_constraint = int(final_constraint)
        return message


# interpret counterpart message 
def interpretation(message):
    global execution_count
    rbai_storage_b2.offer_bot2 = logic_b2.interpret_offer(message, offer_by=rnd_param.role)
    if rbai_storage_b2.offer_list is None:
        rbai_storage_b2.offer_list = OfferList()
    rbai_storage_b2.offer_list.append(rbai_storage_b2.offer_bot2)
    rbai_storage_b2.bot1_message = message
    return evaluate()



# evaluate the offer
def evaluate():
    print('evaluate')
 
    if rbai_storage_b2.offer_list is not None:
        for off in rbai_storage_b2.offer_list:
            logic_b2.add_profits(off)


    greedy = logic_b2.get_greediness(rbai_storage_b2.other_constraint, rnd_param.other_constraint)  
    print(f'greedy: {greedy}') 
    rbai_storage_b2.offers_pareto_efficient = pareto_efficient_string(
        rbai_storage_b2.other_constraint, rbai_storage_b2.main_bot_cons, rnd_param.role_other
    )
    
    evaluation = rbai_storage_b2.offer_bot2.evaluate(greedy)

    if evaluation == ACCEPT:
        return accept_offer()
    elif evaluation in (NOT_PROFITABLE, OFFER_PRICE, OFFER_QUALITY):
        return respond_to_offer(evaluation, greedy)
    elif evaluation in (INVALID_OFFER, NOT_OFFER):
        return respond_to_non_offer(evaluation, greedy)
    else:
        raise Exception


# respond to offer
def respond_to_offer(evaluation: str, greedy: int):
    print(f'respond_to_off with evalutation: {evaluation}')

    content1 = get_respond_prompt(evaluation)

    llm_offers = []
    last_offer = None

    while len(llm_offers) < 3 and evaluation != ACCEPT:
        response = logic_b2.get_llm_response(content1)
        last_offer = logic_b2.interpret_offer(response, offer_by=rnd_param.role_other)

        if last_offer.is_complete:
            logic_b2.add_profits(last_offer)
        else:
            last_offer.profit_bot1 = 0
            last_offer.profit_bot2 = 0

        llm_offers.append([last_offer.profit_bot1, response, last_offer])
        evaluation = last_offer.evaluate(greedy)
        print(f'Evalutation from the while loop: {evaluation}')
        print(f'Offer in offer.py: {OfferList}')
        
    return send_response(evaluation, last_offer, response, llm_offers)


# prompt unprofitable offer
def get_respond_prompt(evaluation: str) -> str:
    if evaluation == FIRST_OFFER:
        return first_offer_prompt(
            rbai_storage_b2.offers_pareto_efficient 
        )
    if evaluation == NOT_OFFER:
        return empty_offer_prompt(
            rbai_storage_b2.bot1_message, rbai_storage_b2.offers_pareto_efficient, str(rbai_storage_b2.interaction_list_bot2)
        )
    elif evaluation == OFFER_QUALITY:
        return offer_without_price_prompt(
            rbai_storage_b2.bot1_message, rbai_storage_b2.offers_pareto_efficient, str(rbai_storage_b2.interaction_list_bot2)
        )
    elif evaluation == OFFER_PRICE:
        return offer_without_quality_prompt(
            rbai_storage_b2.bot1_message, rbai_storage_b2.offers_pareto_efficient, str(rbai_storage_b2.interaction_list_bot2)
        )
    elif evaluation == INVALID_OFFER:
        return offer_invalid(rbai_storage_b2.bot1_message)
    else:
        return not_profitable_prompt(
            rbai_storage_b2.bot1_message, rbai_storage_b2.offers_pareto_efficient, str(rbai_storage_b2.interaction_list_bot2)
        )


# send response
def send_response(evaluation: str, last_offer: Offer,
                  llm_output: str, llm_offers: List[List[Union[int, Any]]]):
    print('send_response')

    if evaluation != ACCEPT:
        max_profit = max(llm_offer[0] for llm_offer in llm_offers)
        best_offer = random.choice([llm_offer for llm_offer in llm_offers
                                    if llm_offer[0] == max_profit])
        _, llm_output, last_offer = best_offer


    if last_offer is not None and last_offer.is_valid:
        if rbai_storage_b2.offer_list is None:
            rbai_storage_b2.offer_list = OfferList()
    if llm_output is not None:
        test = PROMPTS['return_same_message'] % llm_output
        return test


# accept the bots offer
def accept_offer():
    print('accept')
    content = PROMPTS['accept_from_chat'] + rbai_storage_b2.bot1_message
    rbai_storage_b2.end_convo = True

    return content



# no offer provided prompt
def respond_to_non_offer(evaluation: str, greedy: int):
    print(f'respond_to_non_off with evalutation: {evaluation}')
    
    content1 = get_respond_prompt(evaluation)

    llm_offers = []
    last_offer = None

    while len(llm_offers) < 3 and evaluation != ACCEPT:
        response = logic_b2.get_llm_response(content1)
        last_offer = logic_b2.interpret_offer(response, offer_by=rnd_param.role_other)

        if last_offer.is_complete:
            logic_b2.add_profits(last_offer)
        else:
            last_offer.profit_bot1 = 0 
            last_offer.profit_bot2 = 0

        llm_offers.append([last_offer.profit_bot1, response, last_offer])
        evaluation = last_offer.evaluate(greedy)
        print(f'Evalutation from the while loop: {evaluation}')
        print(f'Offer in offer.py: {Offer}')
        
    return send_response(evaluation, last_offer, response, llm_offers)


# for this condition -> give constraint to the other bot
def provide_constraint():
    give_constraint = PROMPTS['context_constraint'][rnd_param.role]
    message = PROMPTS['give_initial_const'] % (give_constraint, give_constraint, rnd_param.other_constraint) 
    return message

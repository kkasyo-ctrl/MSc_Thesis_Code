from typing import Tuple

from rbai_rbai.offer_b1 import Offer, OfferList
from rbai_rbai.prompts import PROMPTS
from shared.rnd_param import QUALITY_RANGE, PRICE_RANGE

# check if pareto efficient
def pareto_efficient(offer: Offer, all_offers: OfferList) -> bool:

    def coll_abs(o: Offer) -> Tuple[int, int]:
        return o.profit_bot2 + o.profit_bot1, abs(o.profit_bot2 - o.profit_bot1)

    collective_profit, abs_difference = coll_abs(offer)  

    for other_offer in all_offers:
        if offer == other_offer:  
            continue
        other_collective_profit, other_abs_difference = coll_abs(other_offer)

        if other_collective_profit > collective_profit and \
                other_abs_difference <= abs_difference:
            return False
        if other_collective_profit >= collective_profit and \
                other_abs_difference < abs_difference:
            return False
    return True  

# generate all pareto efficient offers
def get_efficient_offers(constraint_bot2: int,
                         constraint_bot: int,
                         bot_role: str) -> OfferList:

    offer_list = OfferList()  
    for price in PRICE_RANGE: 
        for quality in QUALITY_RANGE: 
            offer = Offer(price=price, quality=quality, idx=0)
            offer.profits(bot_role, constraint_bot2, constraint_bot)  
            offer_list.append(offer)

    efficient_offer_list = OfferList()
    for offer in offer_list:
        if pareto_efficient(offer, offer_list):  
            efficient_offer_list.append(offer)

    return efficient_offer_list  


def pareto_efficient_offer(constraint_bot2: int,
                           constraint_bot: int,
                           bot_role: str,
                           max_greedy: bool) -> int:

    efficient_offers_for_bot = \
        get_efficient_offers(constraint_bot2, constraint_bot, bot_role)

    if max_greedy:
        return efficient_offers_for_bot.max_profit  
    else:
        return efficient_offers_for_bot.min_profit  


# get pareto efficient strings
def pareto_efficient_string(constraint_bot2: int,
                            constraint_bot: int,
                            bot_role: str) -> str:

    efficient_offers_for_bot = get_efficient_offers(
        constraint_bot2, constraint_bot, bot_role)

    profits_bot = [offer.profit_bot1 for offer in efficient_offers_for_bot]  
    max_profit_bot = max(profits_bot)  

    best_offers = [o for o in efficient_offers_for_bot
                   if o.profit_bot1 == max_profit_bot]


    return ' | '.join(
        PROMPTS['offer_string'] % (o.price, o.quality) for o in best_offers)

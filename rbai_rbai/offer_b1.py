import time  
from typing import Any, Union 

from shared import rnd_param

# constants for different offer evaluations
ACCEPT = 'accept'
NOT_PROFITABLE = 'not_profitable'
OFFER_QUALITY = 'offer_quality'
OFFER_PRICE = 'offer_price'
NOT_OFFER = 'not_offer'
INVALID_OFFER = 'invalid_offer'

# offer object - represents an offer as class
class Offer(dict):  
    def __init__(self,
                 idx: int = -1,
                 price: int = None,  
                 quality: int = None,
                 offer_by: str = None,  
                 stamp: int = None,  
                 from_chat: bool = False,
                 enhanced: str = None,  
                 profit_bot1: int = None, 
                 profit_bot2: int = None, 
                 test: Any = None):  
        stamp = stamp or int(time.time())  
        dict.__init__(self, idx=idx, price=price, quality=quality, offer_by = offer_by,
                      stamp=stamp, from_chat=from_chat, enhanced=enhanced,
                      profit_bot1=profit_bot1, profit_bot2=profit_bot2,
                      test=test)
        self.idx = idx
        self.price = price
        self.quality = quality
        self.offer_by = offer_by
        self.stamp = stamp
        self.from_chat = True 
        self.enhanced = enhanced
        self.profit_bot1 = profit_bot1
        self.profit_bot2 = profit_bot2

    def __getattr__(self, attr): 
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    @property
    def specifics(self) -> str:  
        return f"P+Q = {str(self.price):4} + {str(self.quality):4} ; " \
               f"PROF = {str(self.profit_bot1):3} + {str(self.profit_bot2):3} ;"

    @property
    def is_valid(self) -> bool:  
        return self.is_complete and self.price_in_range and self.quality_in_range

    @property
    def is_complete(self) -> bool:  
        return None not in (self.price, self.quality)

    @property
    def price_in_range(self) -> bool: 
        return self.price in rnd_param.PRICE_RANGE

    @property
    def quality_in_range(self) -> bool: 
        return self.quality in rnd_param.QUALITY_RANGE

    def profits(self, bot_role: str, constraint_bot2: int, constraint_bot: int):
        """Calculate profits for the bot and the bot2."""
        if not self.is_valid or None in (constraint_bot2, constraint_bot):
            self.profit_bot1 = -10
            self.profit_bot2 = -10
            return

        if bot_role == 'supplier':
            self.profit_bot1 = self.profit_supplier(self.price, self.quality, constraint_bot)
            self.profit_bot2 = self.profit_buyer(self.price, self.quality, constraint_bot2)
        else:  # ROLE_BUYER
            self.profit_bot1 = self.profit_buyer(self.price, self.quality, constraint_bot)
            self.profit_bot2 = self.profit_supplier(self.price, self.quality, constraint_bot2)

    def evaluate(self, greedy: int) -> str:
        """Evaluate the offer against bot's greediness."""
        if self.profit_bot1 >= greedy:
            return ACCEPT
        elif self.is_valid:
            return NOT_PROFITABLE
        elif self.price is None and self.quality_in_range:
            return OFFER_QUALITY
        elif self.quality is None and self.price_in_range:
            return OFFER_PRICE
        elif self.price is not None and not self.price_in_range:
            return INVALID_OFFER
        elif self.quality is not None and not self.quality_in_range:
            return INVALID_OFFER
        else:
            return NOT_OFFER

    @staticmethod
    def profit_supplier(price: int, quality: int, production_cost: int) -> int:
        """Calculate profit for supplier."""
        return price - production_cost - quality

    @staticmethod
    def profit_buyer(price: int, quality: int, retail_price: int) -> int:
        """Calculate profit for buyer."""
        return retail_price - price + quality

class OfferList(list):   
    def __init__(self, *args):
        list.__init__(self, *args)  
        self.sort(key=lambda o: o.stamp)  

    def last_valid_price(self, idx: int = None) -> int:
        """Get the last valid price."""
        for offer in sorted(self, key=lambda o: -o.stamp):  
            if idx is not None and offer.idx != idx:  
                continue
            if offer.price is not None:
                return offer.price
        return 5  

    def last_valid_quality(self, idx: int = None) -> int:
        """Get the last valid quality."""
        for offer in sorted(self, key=lambda o: -o.stamp):  
            if idx is not None and offer.idx != idx:  
                continue
            if offer.quality is not None:
                return offer.quality
        return 2  

    @property
    def max_profit(self) -> int:
        """Get the maximum bot profit."""
        if len(self) == 0:
            return 0
        return max([offer.profit_bot1 for offer in self if offer.idx != -1])

    @property
    def min_profit(self) -> int:
        """Get the minimum bot profit."""
        if len(self) == 0:
            return 0
        return min([offer.profit_bot1 for offer in self if offer.idx != -1])

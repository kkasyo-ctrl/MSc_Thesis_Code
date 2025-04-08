import random
import os, csv
import shared
from shared import rnd_param

def simulation():

    bot1_role = random.choice(['buyer', 'supplier'])
    bot2_role = 'supplier' if bot1_role == 'buyer' else 'buyer'

    if bot1_role == 'supplier':
        bot1_constraint = random.randint(1,3) 
        bot2_constraint = random.randint(8,10)
    else:  
        bot1_constraint = random.randint(8,10)
        bot2_constraint = random.randint(1,3)

    PRICE_RANGE = rnd_param.PRICE_RANGE
    QUALITY_RANGE = rnd_param.QUALITY_RANGE

    def is_pareto_efficient(offer, all_offers) -> bool:
        def profit(o):
            price, quality = o
            if bot1_role == 'supplier':
                profit_bot1 = price - quality - bot1_constraint
                profit_bot2 = bot2_constraint + quality - price
            else:
                profit_bot2 = price - quality - bot2_constraint
                profit_bot1 = bot1_constraint + quality - price
            return profit_bot1, profit_bot2

        def coll_abs(o):
            p1, p2 = profit(o)
            return (p1 + p2), abs(p2 - p1)

        current_collective, current_diff = coll_abs(offer)

        for other_offer in all_offers:
            if other_offer == offer:
                continue
            other_collective, other_diff = coll_abs(other_offer)
            if (other_collective > current_collective and other_diff <= current_diff) or \
               (other_collective >= current_collective and other_diff < current_diff):
                return False
        return True  

    def offers():
        pos_offers = []
        efficient_offers = []
        for i in PRICE_RANGE:
            for j in QUALITY_RANGE:
                pos_offers.append((i, j))
        for offer in pos_offers:
            if is_pareto_efficient(offer, pos_offers):
                efficient_offers.append(offer)
        return efficient_offers

    outcomes = offers()

    if outcomes:
        offer_num = random.randint(0, len(outcomes) - 1)
        chosen_offer = outcomes[offer_num]
    else:
        chosen_offer = (None, None)

    return [bot1_role, bot2_role, bot1_constraint, bot2_constraint, chosen_offer[0], chosen_offer[1]]


if __name__ == '__main__':
    total_runs = 800
    results = []

    for run_count in range(total_runs): 
        try:
            row = simulation()
            results.append(row)
        except KeyboardInterrupt:
            print("\nChat interrupted. Exiting.")
            break
        print(f"Completed run {run_count + 1} of {total_runs}")

    # Ensure output directory exists.
    save_path = os.path.join("rb_rb", "output.csv")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=",")
        for row in results:
            writer.writerow(row)

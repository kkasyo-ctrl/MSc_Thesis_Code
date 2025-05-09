# control file
from rb_llm.storage import rb_storage
from rb_llm import analyze_message
from rb_llm.offer import OfferList
from rb_llm import generate_responses

# control function which should be evoked by rb
execution_count = 0
def incoming_message(message):
    global execution_count
    if execution_count == 0:
        msg = generate_responses.initial_message()
        execution_count += 1
        return msg
    
    elif execution_count == 1:
        msg = analyze_message.augment_message(message)
        execution_count += 1
        return msg
    
    elif execution_count == 2:
        msg = analyze_message.constraint_final(message)
        execution_count += 1
        return msg
    
    elif execution_count == 3:
        rb_storage.offer_bot2 = analyze_message.interpret_offer(message)
        if rb_storage.offer_list is None:
            rb_storage.offer_list = OfferList()
            rb_storage.offer_list.append(rb_storage.offer_bot2)
            rb_storage.user_message = message
        execution_count += 1
        msg = generate_responses.evaluate()
        
        # ending mechanism
        if rb_storage.end_convo:
            return msg
        else:
            return msg
    else:
        
        # check if accepted by counterparty
        final_msg = analyze_message.check_offer_acceptance(message)
        if rb_storage.end_convo:
            rb_storage.offer_list.append(rb_storage.offer_bot1)
            for off in rb_storage.offer_list:
                generate_responses.add_profits(off)
            return final_msg
        else:
        
        # try to accept the offer yourself
            rb_storage.offer_bot2 = analyze_message.interpret_offer(message)
            rb_storage.offer_list.append(rb_storage.offer_bot2)
            rb_storage.user_message = message
            msg = generate_responses.evaluate()
            
            # ending mechanism
            if rb_storage.end_convo:
                return msg
            else:
                return msg




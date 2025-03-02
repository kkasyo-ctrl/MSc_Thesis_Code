# control file
from rule_based.storage import rb_storage
from rule_based import analyze_message
from rule_based.offer import OfferList
from rule_based import generate_responses


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
        rb_storage.offer_user = analyze_message.interpret_offer(message)
        if rb_storage.offer_list is None:
            rb_storage.offer_list = OfferList()
            rb_storage.offer_list.append(rb_storage.offer_user)
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
        analyze_message.check_offer_acceptance(message)
        if rb_storage.end_convo:
            return "End of conversation"
        else:
        # try to accept the offer yourself
            rb_storage.offer_user = analyze_message.interpret_offer(message)
            msg = generate_responses.evaluate()
            # ending mechanism
            if rb_storage.end_convo:
                return msg
            else:
                return msg




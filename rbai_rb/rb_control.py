# control file
from rbai_rb.rb_storage import rb_storage
from rbai_rb import analyze_message
from rbai_rb.offer_rbai import OfferList
from rbai_rb import generate_responses


execution_count = 0
def incoming_message(message):
    global execution_count
    if execution_count == 0:
        msg = generate_responses.give_const(message)
        execution_count += 1
        return msg
    
    elif execution_count == 1:
        msg = analyze_message.augment_message(message)
        execution_count += 1
        return msg

    elif execution_count == 2:
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
            rb_storage.offer_list.append(rb_storage.offer_user)
            rb_storage.user_message = message
            msg = generate_responses.evaluate()
            # ending mechanism
            if rb_storage.end_convo:
                return msg
            else:
                return msg




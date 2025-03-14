# messages
MESSAGES = {
    'first_message_PC': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?",
    'offer_string': "Price of %s€ and quality of %s",
    'first_message_RP': "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price to Consumer?",
    
    'context_constraint': {
        'buyer': 'Base Production Cost (PC)',
        'supplier': 'Base Retail Price to Consumer (RP)',
    },

    'constraint_clarify':
        'I did not quite understand. Please clarify your current %s at the quality level of 0.\n',

    'constraint_not_found':
        'I could not find the %s in your message. Please provide it again.\n',

    'constraint_confirm':
        'Confirming: Is %s the correct %s?\n'
        'If it is correct, please ONLY enter %s again in the chat bellow.\n'
        'Otherwise enter your current %s at the quality level of 0.\n',

    'constraint_persist_final_buyer':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Retail Prices to Consumers has values between 8 and 10. Thus, I will assume your actual value is 10. \n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag?'
        'Please return only one offer with the Wholesale Price and Quality you have in mind, mentioning both only once.',

    'constraint_persist_final_supplier':
        'My apologies for persisting.\n'
        'Note: My data regarding the normal range of Base Production Cost has values between 1 and 3. Thus, I will assume your actual value is 1. \n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag?'
        'Please return only one offer with the Wholesale Price and Quality you have in mind, mentioning both only once.',
    
    'constraint_final_buyer':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to purchase a 10kg pellet bag? '
        'Please return only one offer with the Wholesale Price and Quality you have in mind, mentioning both only once.',
    
    'constraint_final_supplier':
        'Thanks, for confirming this information with me.\n'
        'What combination of Price and Quality do you have in mind '
        'to sell me a 10kg pellet bag? '
        'Please return only one offer with the Wholesale Price and Quality you have in mind, mentioning both only once.',    

    'accept_offer': 
        'I am pleased to accept your offer! Thank you for negotiating with us! I appreciate your understanding and look forward to a successful partnership.',
    
    'they_accept_offer': 
        'Thank you for negotiating with us! We are looking forward to a successful partnership.',
    
    'respond_to_offer':
        'I appreciate your offer, but I am looking for a different combination of Price and Quality. How about Wholesale %s?',

    'respond_to_non_offer':
        'I am sorry, but your offer is not valid. This is either because I did not recognize it, proposed terms were out of bounds or price or quality were not integers. How about Wholesale %s?',

    'initial_offer':
        'I would like to propose %s. Does that work for you?',


}

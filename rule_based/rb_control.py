# control file
from shared import rb_storage

def initial_message():
    if rb_storage.bot_role == "buyer":
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Production Cost?"
    else:
        message = "Hi! I'm excited to start our negotiation. As we begin, I'd like to get a sense of your needs and constraints. Can you share with me your Base Retail Price?"

    return message

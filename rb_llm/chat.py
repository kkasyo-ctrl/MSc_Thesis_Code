import json
import os
import sys
import requests
import datetime
from rb_llm import rb_control 
from rb_llm.storage import rb_storage, saving_convo
from shared import rnd_param 
from rb_llm.message_storage import system_final_prompt

# LLM-based chat function with streaming output
def _chat_to_ai(conversation_history, ai_number, mod_used, temperature=0.1):
    response_chat = {
        "role": "assistant",
        "content": "",
        "options": {
            "temperature": temperature,
        }
    }

    headers = {'Content-Type': 'application/json'}

    if mod_used == 'llama3':
        llm_mod = 'llama3:latest'
    elif mod_used == 'llm_reader':
        llm_mod = 'reader:latest'
    elif mod_used == 'llm_constraint':
        llm_mod = 'constrain_reader:latest'
    else:
        llm_mod = 'llama3:latest'

    ollama_payload = {
        "model": llm_mod,
        "messages": conversation_history
    }

    try:
        response = requests.post('http://localhost:11434/api/chat', 
                                 data=json.dumps(ollama_payload), headers=headers,
                                 stream=True)

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    chat_response = json.loads(decoded_line)
                    chat_message = chat_response['message']['content']
                    response_chat['content'] += chat_message
                    print(chat_message, end='', flush=True)
                    if chat_response.get('done', False):
                        break
            print("")  
        else:
            print('Failed to send chat request.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)
            response_chat['content'] = "Error: Failed to get response."
    except requests.exceptions.RequestException as e:
        print('Failed to send chat request.')
        print('Error:', e)
        response_chat['content'] = 'Failed to send chat request.'

    return response_chat

# Rule–based (non LLM) bot's response function.
def non_llm_response(last_message):
    msg = rb_control.incoming_message(last_message)
    return msg 

# negotiation loop
def run_chat_interaction(num_turns=20):
    conversation_history = []
    
    # context for LLM
    syst_txt = system_final_prompt()
    system_message = {"role": "system", "content": syst_txt}
    conversation_history.append(system_message)
    
    
    # initial message
    initial_rule_message = {"role": "user", "content": non_llm_response("text")}
    conversation_history.append(initial_rule_message)
    
    chat_counter = 1
    num_turns = 20 

    print(f"({chat_counter} of {num_turns}) {rnd_param.role_other}: \n",initial_rule_message['content'])
    
    
    rb_storage.interaction_list_bot1 = []
    rb_storage.interaction_list_bot2 = []
    rb_storage.interaction_list_bot2.append({
        'role': 'user',
        'content': initial_rule_message['content']
        })
    rb_storage.interaction_list_bot1.append({
        'role': 'assistant',
        'content': initial_rule_message['content']
        })
    
 

    while rb_storage.end_convo == False and chat_counter <= int(num_turns):
        chat_counter += 1
        if chat_counter % 2 == 0:  
            print("\n({} of {}) {}:".format(chat_counter, num_turns, rb_storage.bot2_role))
            ai_response = _chat_to_ai(conversation_history, ai_number=1, mod_used='llama3', temperature=0.1)
            llm_msg = ai_response['content'].strip()

            conversation_history.append({"role": "assistant", "content": llm_msg})


            rb_storage.interaction_list_bot1.append({
                'role': 'user',
                'content': llm_msg
            })
            
            rb_storage.interaction_list_bot2.append({
                'role': 'assistant',
                'content': llm_msg
            })

        else: 
            print("\n({} of {}) {}:".format(chat_counter, num_turns, rb_storage.bot1_role))
            rb_msg = non_llm_response(conversation_history[-1]['content'])
            print(rb_msg)
            conversation_history.append({"role": "user", "content": rb_msg})
            
            rb_storage.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rb_msg
            })

            rb_storage.interaction_list_bot2.append({
                'role': 'user',
                'content': rb_msg
            })



    # save the conversation to a file.
    saving_convo()
    save_file_name = 'chat_history/ai_chat_{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    save_path = os.path.join("rb_llm", save_file_name)
    with open(save_path, 'w') as f:
        json.dump(conversation_history, f, indent=4)
    print("\nConversation saved to", save_path)

if __name__ == '__main__':
    try:
        run_chat_interaction(num_turns=10)
    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")
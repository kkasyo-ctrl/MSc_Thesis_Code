import json
import os
import sys
import requests
import datetime
import copy
from rbai_rb import rb_control 
from rbai_rb import activation
from rbai_rb.rbai_storage import rbai_storage, saving_convo
from rbai_rb.rb_storage import rb_storage
from shared import rnd_param 
from rbai_rb.prompts import system_final_prompt

# ensure encoding is utf-8
sys.stdout.reconfigure(encoding='utf-8')

# LLM-based chat function with streaming output
def _chat_to_ai(conversation_history, mod_used, temperature=0.1):
    response_chat = {
        "role": "assistant",
        "content": "",
        "options": {
            "temperature": temperature,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }
    
    # determine the model type
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
    conversation_history1 = []
    
    # context for LLM
    syst_txt = system_final_prompt()

    
    system_message = {"role": "system", "content": syst_txt}
    conversation_history1.append(system_message)

    # initial message    
    initial_msg = activation.initial()
    init_mod = {"role": "assistant", "content": initial_msg}
    conversation_history1.append(init_mod)
    
    
    chat_counter = 1
    num_turns = 20 
    print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage.bot1_role))
    print(initial_msg)
    
    rbai_storage.interaction_list_bot1 = []
    rbai_storage.interaction_list_bot2 = []
    rbai_storage.interaction_list_bot2.append({
        'role': 'user',
        'content': initial_msg
        })
    rbai_storage.interaction_list_bot1.append({
        'role': 'assistant',
        'content': initial_msg
        })
    
    rb_storage.interaction_list_bot1 = []
    rb_storage.interaction_list_bot2 = []
    rb_storage.interaction_list_bot2.append({
        'role': 'user',
        'content': initial_msg
        })
    rb_storage.interaction_list_bot1.append({
        'role': 'assistant',
        'content': initial_msg
        })

    # fix while loop
    while rbai_storage.end_convo == False and chat_counter < int(num_turns):
        chat_counter += 1
        if chat_counter % 2 == 1:  
            
            
            modified_content = activation.modify_bot_message(rb_msg)
            tmp_conversation_history = copy.deepcopy(conversation_history1)
            tmp_conversation_history[-1]['content'] += modified_content

            print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage.bot1_role))
            mod = "llama3"
            rbai_response = _chat_to_ai(tmp_conversation_history, mod, temperature=0.1)
            rbai_msg = rbai_response['content'].strip()
            
            conversation_history1.append({"role": "assistant", "content": rbai_msg})

            rbai_storage.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msg
            })
            
            rbai_storage.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msg
            })

            rb_storage.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msg
            })
            
            rb_storage.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msg
            })

        else: 
            print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage.bot2_role))
            rb_msg = non_llm_response(conversation_history1[-1]['content'])
            print(rb_msg)
            conversation_history1.append({"role": "user", "content": rb_msg})

            rbai_storage.interaction_list_bot1.append({
                'role': 'user',
                'content': rb_msg
            })

            rbai_storage.interaction_list_bot2.append({
                'role': 'assistant',
                'content': rb_msg
            })

            rb_storage.interaction_list_bot1.append({
                'role': 'user',
                'content': rb_msg
            })

            rb_storage.interaction_list_bot2.append({
                'role': 'assistant',
                'content': rb_msg
            })


    # save the conversation to a file.
    saving_convo()
    save_file_name = 'chat_history/ai_chat_{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    save_path = os.path.join("rbai_rb", save_file_name)
    with open(save_path, 'w') as f:
        json.dump(conversation_history1, f, indent=4)
    print("\nConversation saved to", save_path)

if __name__ == '__main__':
    try:
        run_chat_interaction(num_turns=10)
    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")
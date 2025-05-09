import json
import os
import sys
import requests
import datetime
import copy
from rbai_rbai.rbai_storage_b1 import rbai_storage_b1, saving_convo
from rbai_rbai.rbai_storage_b2 import rbai_storage_b2
from shared import rnd_param 
from rbai_rbai.prompts import system_final_prompt1, system_final_prompt2

# ensure correct encoding 
sys.stdout.reconfigure(encoding='utf-8')

# LLM call/dump json function 
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

from rbai_rbai import activation_b1
from rbai_rbai import activation_b2

# negotiation loop
def run_chat_interaction(num_turns=20):
    conversation_history1 = []
    conversation_history2 = []
    
    # context for LLM
    syst_txt1 = system_final_prompt1()
    syst_txt2 = system_final_prompt2()

    
    system_message1 = {"role": "system", "content": syst_txt1}
    system_message2 = {"role": "system", "content": syst_txt2}
    conversation_history1.append(system_message1)
    conversation_history2.append(system_message2)


    # initial message    
    rbai_msgb1  = activation_b1.initial()
    
    conversation_history1.append({"role": "assistant", "content": rbai_msgb1 })
    conversation_history2.append({"role": "user", "content": rbai_msgb1 })

    
    chat_counter = 1
    num_turns = 20 
    print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage_b1.bot1_role))
    print(rbai_msgb1)
    
    rbai_storage_b1.interaction_list_bot1 = []
    rbai_storage_b1.interaction_list_bot2 = []
    rbai_storage_b1.interaction_list_bot2.append({
        'role': 'user',
        'content': rbai_msgb1
        })
    rbai_storage_b1.interaction_list_bot1.append({
        'role': 'assistant',
        'content': rbai_msgb1
        })
    
    rbai_storage_b2.interaction_list_bot1 = []
    rbai_storage_b2.interaction_list_bot2 = []
    rbai_storage_b2.interaction_list_bot2.append({
        'role': 'user',
        'content': rbai_msgb1
        })
    rbai_storage_b2.interaction_list_bot1.append({
        'role': 'assistant',
        'content': rbai_msgb1
        })

    # negotiation while loop
    while rbai_storage_b1.end_convo == False and rbai_storage_b2.end_convo == False and chat_counter < int(num_turns):
        chat_counter += 1
        if chat_counter % 2 == 1:  
            modified_content = activation_b1.modify_bot_message(rbai_msgb2)
            tmp_conversation_history = copy.deepcopy(conversation_history1)
            tmp_conversation_history[-1]['content'] += modified_content

            print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage_b1.bot1_role))
            mod = "llama3"
            rbai_response = _chat_to_ai(tmp_conversation_history, mod, temperature=0.1)
            rbai_msgb1 = rbai_response['content'].strip()
            
            conversation_history1.append({"role": "assistant", "content": rbai_msgb1})
            conversation_history2.append({"role": "user", "content": rbai_msgb1})

            rbai_storage_b1.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msgb1
            })
            
            rbai_storage_b1.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msgb1
            })

            rbai_storage_b2.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msgb1
            })
            
            rbai_storage_b2.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msgb1
            })

        else: 

            modified_content = activation_b2.modify_bot_message(rbai_msgb1)
            tmp_conversation_history = copy.deepcopy(conversation_history2)
            tmp_conversation_history[-1]['content'] += modified_content

            print("\n({} of {}) {}:".format(chat_counter, num_turns, rbai_storage_b2.bot2_role))
            mod = "llama3"
            rbai_response = _chat_to_ai(tmp_conversation_history, mod, temperature=0.1)
            rbai_msgb2 = rbai_response['content'].strip()
            
            conversation_history2.append({"role": "assistant", "content": rbai_msgb2})
            conversation_history1.append({"role": "user", "content": rbai_msgb2})

            rbai_storage_b1.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msgb2
            })
            
            rbai_storage_b1.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msgb2
            })

            rbai_storage_b2.interaction_list_bot1.append({
                'role': 'assistant',
                'content': rbai_msgb2
            })
            
            rbai_storage_b2.interaction_list_bot2.append({
                'role': 'user',
                'content': rbai_msgb2
            })

    # save the conversation to a file.
    saving_convo()
    save_file_name = 'chat_history/ai_chat_{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    save_path = os.path.join("rbai_rbai", save_file_name)
    with open(save_path, 'w') as f:
        json.dump(conversation_history1, f, indent=4)
    print("\nConversation saved to", save_path)

if __name__ == '__main__':
    try:
        run_chat_interaction(num_turns=10)
    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")
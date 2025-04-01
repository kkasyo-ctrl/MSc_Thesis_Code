import json
import os
import requests
import datetime
from llm_llm.storage import llm_storage
from llm_llm.storage import extract_price_and_quality, calculate_profits, saving_convo
from llm_llm.mediator_prompts import PROMPTS, system_final_prompt_role, system_final_prompt_role_other
from shared import rnd_param 

# LLM-based chat function with streaming output (unchanged)
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
                    # Stream output in real time:
                    print(chat_message, end='', flush=True)
                    if chat_response.get('done', False):
                        break
            print("")  # newline after response
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


# negotiation loop
def run_chat_interaction(num_turns=20):
    conversation_history1 = []
    conversation_history2 = []
    
    # supplier/buyer system messages
    bot1_system = system_final_prompt_role()
    bot2_system = system_final_prompt_role_other()

    system_message1 = {"role": "system", "content": bot1_system}
    system_message2 = {"role": "system", "content": bot2_system}
    
    conversation_history1.append(system_message1)
    conversation_history2.append(system_message2)
    
    initial_message = "Let's start the negotiation."
    conversation_history1.append({"role": "user", "content": initial_message})
    conversation_history2.append({"role": "assistant", "content": initial_message})
    
    llm_storage.interaction_list_bot1 = []
    llm_storage.interaction_list_bot2 = []
    llm_storage.interaction_list_bot2.append({
        'role': 'user',
        'content': initial_message
        })
    llm_storage.interaction_list_bot1.append({
        'role': 'assistant',
        'content': initial_message
        })

    chat_counter = 1
    num_turns = 10  # total number of negotiation turns


    ai_eval = 'CONTINUE'
    # interaction loop
    while ai_eval == "CONTINUE" and chat_counter < int(num_turns):
        if chat_counter >= 3:
            check_status_prompt = PROMPTS['evalutate_conversation'] % conversation_history1[-4:]
            eval_history = [{"role": "system", "content": check_status_prompt}]
            ai_response = _chat_to_ai(eval_history, ai_number=1, mod_used='llama3', temperature=0.1)
            ai_eval = ai_response['content'].strip()

        if ai_eval == "CONTINUE":
            if chat_counter % 2 == 1:             
                print("\n({} of {}) {}:".format(chat_counter, num_turns, rnd_param.role))
                ai_response = _chat_to_ai(conversation_history1, ai_number=1, mod_used='llama3', temperature=0.1)
                bot1msg = ai_response['content'].strip()

                conversation_history1.append({"role": "assistant", "content": bot1msg})
                conversation_history2.append({"role": "user", "content": bot1msg})
                
                llm_storage.interaction_list_bot1.append({
                    'role': 'user',
                    'content': bot1msg
                })
                
                llm_storage.interaction_list_bot2.append({
                    'role': 'assistant',
                    'content': bot1msg
                })

            else: 
                print("\n({} of {}) {}:".format(chat_counter, num_turns, rnd_param.role_other))
                ai_response = _chat_to_ai(conversation_history2, ai_number=2, mod_used='llama3', temperature=0.1)
                bot2msg = ai_response['content'].strip()
                conversation_history1.append({"role": "user", "content": bot2msg})
                conversation_history2.append({"role": "assistant", "content": bot2msg})
                
                llm_storage.interaction_list_bot1.append({
                    'role': 'assistant',
                    'content': bot2msg
                })

                llm_storage.interaction_list_bot2.append({
                    'role': 'user',
                    'content': bot2msg
                })

            chat_counter += 1

    # find agreement
    find_outcomes = PROMPTS['find_outcomes'] % conversation_history1[-4:]
    extract_message = [{"role": "system", "content": find_outcomes}]
    ai_response = _chat_to_ai(extract_message, ai_number=1, mod_used='llama3', temperature=0.1)
    agreed_pq = ai_response['content'].strip()
    llm_storage.agreed_price , llm_storage.agreed_quality = extract_price_and_quality(agreed_pq)
    
    # count offers
    find_outcomes = PROMPTS['count_offers'] % conversation_history1
    extract_message = [{"role": "system", "content": find_outcomes}]
    ai_response = _chat_to_ai(extract_message, ai_number=1, mod_used='llama3', temperature=0.1)
    num_off = ai_response['content'].strip()
    llm_storage.num_off = int(num_off)


    # caclulate profits
    calculate_profits()

    # save conversation
    saving_convo()

    save_file_name = 'chat_history\\ai_chat_{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    save_path = os.path.join("llm_llm", save_file_name)
    # Write as plain text
    with open(save_path, 'w', encoding='utf-8') as f:
        for msg in conversation_history1:
            f.write(f"{msg['role']}: {msg['content']}\n\n")
    print("\nConversation saved to", save_path)
    


if __name__ == '__main__':
    try:
        run_chat_interaction(num_turns=10)
    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")

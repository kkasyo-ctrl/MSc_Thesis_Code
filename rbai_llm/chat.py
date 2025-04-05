import datetime # used to generate timestamps
import requests # making HTTP requests to ollama api
import json # reading javescript object notation
import sys # for command-line arguments and I/O encoding.
import os 
from rbai_llm import activation 
from rbai_llm import system_info
from shared import rnd_param
import copy
from rbai_llm.prompts import system_final_prompt, system_final_prompt_other

# ensure encoding is utf-8
sys.stdout.reconfigure(encoding='utf-8')

init_chist = 0


# check available models; if error list available models
def _get_List_of_downloaded_models():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get('http://localhost:11434/api/tags', headers=headers)
        if response.status_code == 200:
            models = response.json()
            # check if models is a dictionary
            if isinstance(models, dict):
                model_name_List = []
                for model in models['models']:
                    model_name_List.append(model['name'])
                return model_name_List
            else:
                print('Failed to get list of models.')
                print('Response:', response.text)
                return []
        else:
            print('Failed to get list of models.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('Failed to get list of models.')
        print('Error:', e)
        return []


# checks if a given model_name is present in downloaded models
def _is_model_available(model_name):
    models = _get_List_of_downloaded_models()
    if model_name in models:
        return True
    return False


# sends a conversation prompt/history to the Ollama endpoint (/api/chat) and streams the response
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

    # Send the chat request with history
    ollama_payload = {
        "model": llm_mod,
        "messages": conversation_history
    }

    try:
        response = requests.post('http://localhost:11434/api/chat', data=json.dumps(ollama_payload), headers=headers,
                                 stream=True)
  
        if response.status_code == 200:

            # Handle the stream of responses
            formatted_chat_text = ''
            for line in response.iter_lines():
                # Filter out keep-alive new lines
                if line:
                    decoded_line = line.decode('utf-8')
                    chat_response = json.loads(decoded_line)
                    chat_message = chat_response['message']['content']
                    response_chat['content'] += chat_message

                    print(chat_message, end='', flush=True)
                    formatted_chat_text += chat_message

                    # Check if the conversation is done
                    if chat_response.get('done', False):
                        break
        else:
            print('Failed to send chat request.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('Failed to send chat request.')
        print('Error:', e)
        response_chat['content'] = 'Failed to send chat request.'

    return response_chat


def _chat_run(conversation_history, ai_number, ai_display_name, ai_other_number, counter, ai_chat):    

    # hard coded messages bot 2 to improve performance
    if ai_number == 2 and (counter == 1 or counter == 3):
        print('\n\n')
        custom_message = {
            "role": "assistant",
            "content": conversation_history[2][-1]['content']
        }
        conversation_history[2] = copy.deepcopy(system_info.Storage.interaction_list_bot2)

        # Append the custom message to Bot 2's conversation history.
        conversation_history[ai_number].append(custom_message)
        
        ai_other_message = custom_message.copy()
        ai_other_message['role'] = 'user'
        conversation_history[ai_other_number].append(ai_other_message)
        print(conversation_history[2][-1]['content'])
        
        return  
    
    model_used = 'llama3'
    
    
    ai_response = _chat_to_ai(conversation_history[ai_number], model_used, ai_chat['temperature'])
    ai_message = ai_response


    conversation_history[2] = copy.deepcopy(system_info.Storage.interaction_list_bot2)


    # Depending on which bot is sending, add the message to the proper conversation histories:
    if ai_number == 1:
        conversation_history[ai_number].append(ai_message)
        original_content = ai_message['content']
        modified_content = activation.modify_bot_message(original_content)
        ai_other_message = {
            'role': 'user',
            'content': modified_content
        }
        conversation_history[ai_other_number].append(ai_other_message)
    else:
        conversation_history[ai_number].append(ai_message)
        ai_other_message = ai_message.copy()
        ai_other_message['role'] = 'user'
        conversation_history[ai_other_number].append(ai_other_message)



def run_chat_interaction(ai_chat):
    try:
        # Check if the models are available
        if not _is_model_available(ai_chat['ai_one_model']):
            print(
                'AI One model "{}" is not available. Please download the model first or alter the config file to use one of these models:'.format(
                    ai_chat['ai_one_model']))
            for model in _get_List_of_downloaded_models():
                print('   ' + model)
            return
        if not _is_model_available(ai_chat['ai_two_model']):
            print(
                'AI Two model "{}" is not available. Please download the model first or alter the config file to use one of these models:'.format(
                    ai_chat['ai_two_model']))
            for model in _get_List_of_downloaded_models():
                print('   ' + model)
            return


            # Print the AI display names by using a list, so we can easily switch between the two AIs using 1 or 2
            # for AI One or AI Two
        ai_display_name = [None, ai_chat['ai_one_conversation_history'][0]['display_name'],
                           ai_chat['ai_two_conversation_history'][0]['display_name']]


        print('(First chat output may be delayed while AI model is loaded...)')

        # by storing the conversation history in a list, we can easily switch between the two AIs: 1 or 2 for AI One or AI Two
        conversation_history = [None, ai_chat['ai_one_conversation_history'], ai_chat['ai_two_conversation_history']]
        
        chatting_to_ai_one = True
        chat_counter = 0
        
        copied_start = ai_chat['ai_two_conversation_history'].copy()
        copied_start2 = ai_chat['ai_one_conversation_history'].copy()
        part_copied1 = ai_chat['ai_one_conversation_history'][-1]['content'][:]

        global init_chist
        if init_chist == 0:
            system_info.Storage.interaction_list_bot2 = []
            system_info.Storage.interaction_list_bot2.extend(copied_start)
            system_info.Storage.interaction_list_bot2.append({
                        'role': 'assistant',
                        'content': part_copied1
                    })
            system_info.Storage.interaction_list_bot1 = []
            system_info.Storage.interaction_list_bot1.extend(copied_start2)
            init_chist = 1

        print('Chatting with {} and {}...\n'.format(ai_display_name[1], ai_display_name[2]))
        print('First message from {} to {} is: {} '.format(ai_display_name[2], ai_display_name[1], ai_chat_config["ai_one_conversation_history"][1]["content"] ))

        while chat_counter < int(ai_chat['number_of_chat_turns']):

            ai_number = 1 if chatting_to_ai_one else 2
            ai_other_number = 2 if chatting_to_ai_one else 1

            # Time to say goodbye
            if chat_counter >= int(ai_chat['number_of_chat_turns']) - 2:
                conversation_history[ai_number].append(ai_chat['ai_final_chat_message'][str(ai_other_number)])            

            # store clean conversation history
            if chat_counter > 0:
                if ai_number == 2:
                    temp_msg = conversation_history[1][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'user',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                else:
                    temp_msg = conversation_history[2][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'user',
                        'content': temp_msg
                    })
            
            print("\n({} of {}) {}:".format(chat_counter + 1, ai_chat['number_of_chat_turns'], rnd_param.role_other if chatting_to_ai_one else rnd_param.role))

            # Perform a chat - calls interaction !!!
            _chat_run(conversation_history, ai_number, ai_display_name[ai_number], ai_other_number, chat_counter,
                      ai_chat)
                
            if system_info.Storage.end_convo == True:
                chat_counter += 1
                
                
                #### Save chat history
                if ai_number == 1:
                    temp_msg = conversation_history[1][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'user',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                else:
                    temp_msg = conversation_history[2][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'user',
                        'content': temp_msg
                    })
                ####

                _chat_run(conversation_history, ai_other_number, ai_display_name[ai_other_number], ai_number, chat_counter, ai_chat)
                
                if ai_number == 2:
                    temp_msg = conversation_history[1][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'user',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                else:
                    temp_msg = conversation_history[2][-1]['content']
                    system_info.Storage.interaction_list_bot2.append({
                        'role': 'assistant',
                        'content': temp_msg
                    })
                    
                    system_info.Storage.interaction_list_bot1.append({
                        'role': 'user',
                        'content': temp_msg
                    })
                ####


                system_info.saving_convo()
                print("\n\nNegotiation has reached a deal. Ending chat.")

                break  # Exit loop when DEAL is detected

            # Swap AIs
            chatting_to_ai_one = not chatting_to_ai_one
            chat_counter += 1
        
        
    except KeyboardInterrupt:
        print('Chat ended.')
        # create a file name that includes date and time:

    finally:
        print('\n\n')




if __name__ == '__main__':
    if len(sys.argv) > 1:
        ai_chat_file = sys.argv[1] + ('' if sys.argv[1].endswith('.json') else '.json')
    else:
        print('Please specify the AI chat file as a command-line parameter.')
        sys.exit(1)

    ai_chat_file = os.path.join(os.path.dirname(__file__), ai_chat_file)  # Ensure correct path

    with open(ai_chat_file, 'r') as f:
        ai_chat_config = json.load(f)
    
    ai_chat_config['ai_one_conversation_history'][0]['display_name'] = rnd_param.role_other
    ai_chat_config['ai_two_conversation_history'][0]['display_name'] = rnd_param.role
    


    # give prompt dynamically
    if rnd_param.role == 'supplier':
        ai_chat_config['ai_two_conversation_history'][0]['content'] = system_final_prompt()
        ai_chat_config['ai_one_conversation_history'][0]['content'] = system_final_prompt_other()

    else:
        ai_chat_config['ai_two_conversation_history'][0]['content'] = system_final_prompt()
        ai_chat_config['ai_one_conversation_history'][0]['content'] =  system_final_prompt_other()
    
    initial_msg = activation.initial()

    print(ai_chat_config['ai_two_conversation_history'][0]['content'])
    print(ai_chat_config['ai_one_conversation_history'][0]['content'])
     
    # Ensure ai_one_conversation_history has at least two entries
    if len(ai_chat_config["ai_one_conversation_history"]) > 1:
        ai_chat_config["ai_one_conversation_history"][1]["content"] = initial_msg
    else:
        sys.exit(1)
    
    run_chat_interaction(ai_chat_config)


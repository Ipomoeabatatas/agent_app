import os
import inspect
from utils.gmail_authenticator import authenticate_gmail
from langchain_community.tools.gmail.search import GmailSearch
import time
from datetime import datetime
from utils.config_loader import app_config as config
from utils.directory_cleaner import ensure_clean_directory
from email_crew.crew import AiCrew
import shutil


from rag.mail_processor import *
from pprint import pprint

class NodeDefinition:
    def __init__(self):
        self.gmail = authenticate_gmail()
        self.duration = config.LANGCHAIN_WAIT_DURATION
    
    
    def check_state_status(self, node, state):
        print ()
        print ("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")        
        print(f"Node: {node}")
        print("State:")
        pprint(state, indent=4)
        
    def check_email(self, state):
        self.check_state_status( inspect.currentframe().f_code.co_name, state)
        
        state["graph_counter"] = state["graph_counter"] + 1   # Increment the counter
        #print(f"Node: {inspect.currentframe().f_code.co_name}")
        #print("State:")
        #pprint(state, indent=4)

        search = GmailSearch(api_resource=self.gmail.api_resource)
        
        emails = search.invoke('is:unread in:inbox')  # input is must be a valid gmail search query  
        checked_emails = state['checked_emails_ids'] if state['checked_emails_ids'] else []
        thread = []
        new_emails = []
    
        for email in emails:
            if (email['id'] not in checked_emails) and (email['threadId'] not in thread) and ( os.environ['MY_EMAIL'] not in email['sender']):
                thread.append(email['threadId'])
                new_emails.append(
                    {
                        "id": email['id'],
                        "threadId": email['threadId'],
                        "snippet": email['snippet'],
                        "sender": email["sender"],
                        "subject": email["subject"],
                        "from": email["from"],
                        "cc": email["cc"]
                    }
                )
        checked_emails = list(set(checked_emails + [email['id'] for email in emails]))

        return {
            **state,   #expands the current state
            "emails": new_emails,
            "checked_emails_ids": checked_emails,
            
        }

    
    def handoff_to_aicrew(self, state):
        self.check_state_status( inspect.currentframe().f_code.co_name, state)
        mail_crew = AiCrew().crew()
        inputs = {
        'emails': state['emails'],
        }

        try:
            print("Starting Crew AI processing...")
            crew_output=mail_crew.kickoff(inputs=inputs)
            print("Crew AI processing completed. Returning state...")
            print(f"Raw CrewAI Output: {crew_output.raw}")
            return {**state, "action_required_emails": {'dummy': 'dummy'}}
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")
            return {**state}
    
    
    def save_to_kb(self, state):    
        self.check_state_status( inspect.currentframe().f_code.co_name, state)
        
        outputs_crew_dir = config.OUTPUTS_CREW
        valid_jsons = []
        
        '''
        logic:
        1. Extract valid JSONs lines from the crew outputs and rename the subdirectories to end with '-exported'
        2. For every JSON line
            - extract email and attachments into a target directory (save_dir)
            - vectorise the content of the target diretory (save_dir)
            - rename the taget directory (save_directory) to end with '-vectorised'
        
        '''
        
        # 1. Extract valid JSONs from the crew outputs and rename the subdirectories to end with '-exported'
        # output of step 1 as below    
        #  [ {"messageId": "1956fb9c808dfd8e", "threadId": "1956fb9c808dfd8e", "bookingRef": "F45451345A", "status": "DraftCompleted"}  ]
        
        valid_jsons = extract_valid_jsonl(base_dir=outputs_crew_dir, suffix="-exported") 
        rename_subdirectories(base_dir=outputs_crew_dir, suffix="-exported")
    
        #2. Send the valid JSONs to extract out the emails and attachment to rag input folder
        # rag input folder is the input folder for the RAG model and must be empty before the process starts
        # raf input folder can be customised through the config file.
        rag_input_dir = config.LLAMINDEX_INPUTDIR
        ensure_clean_directory(rag_input_dir)
        
        if not valid_jsons:
            print("No valid JSONs found. Skipping email extraction and vectorization.")
            return {**state, "action_required_emails": {'dummy': 'dummy'}}
        
        extract_emails(valid_jsons, rag_input_dir)
        
        #3. Vectorise the contents of the rag input folder 
        vectorize_mails_v2(message_id="not-used", booking_ref="not-used", load_dir=rag_input_dir)
        
        print(f"Completed: exporting and vectorising the emails")
        
        # Copy the emails/attachment to the output directory self.OUTPUTS_RAG
        print(f"Copying the emails/attachment from {rag_input_dir} to {config.OUTPUTS_RAG}")
        #print(f"FROM RAG output directory: {rag_input_dir}")
        #print(f"TO RAG output directory: {config.OUTPUTS_RAG}")
        shutil.copytree(rag_input_dir, config.OUTPUTS_RAG, dirs_exist_ok=True)
    
        return {**state, "action_required_emails": {'dummy': 'dummy'}}
    
    def wait_next_run(self, state):
        self.check_state_status( inspect.currentframe().f_code.co_name, state)
        
        #print(f"Node: {inspect.currentframe().f_code.co_name}")
        #print(f"Waiting for {duration} seconds")
        time.sleep(self.duration)
        return {**state, "action_required_emails": {'dummy': 'dummy'}}

    def end_workflow(self, state):
        self.check_state_status( inspect.currentframe().f_code.co_name, state)
        print ("+++++++++++++++++++++END+++++++++++++++++++++++++++++++++++++++")

    
 
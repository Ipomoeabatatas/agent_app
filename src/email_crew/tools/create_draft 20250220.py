
import json
#from langchain.tools import tool
from crewai.tools import tool
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
import logging
from msg_app.src.utils.gmail_authenticator import authenticate_gmail

## Pydantic Models

from pydantic import ValidationError
from pydantic.v1 import BaseModel, Field, EmailStr
## from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


from email_crew.schemas import  EmailMessage

from langchain_community.agent_toolkits import GmailToolkit

from msg_app.src.utils.old_load_config import load_config
from msg_app.src.utils.gmail_authenticator import authenticate_gmail


class CreateDraftTool:

    @tool("create_draft")
    def create_draft(input_data: EmailMessage) -> str: 
        """
        Creates a draft email using the provided email data.
        Args:
            input_data (EmailMessage): An instance of EmailMessage containing the email details.
                id: str = Field(..., description="Unique identifier for the individual message")
                threadId: str = Field(..., description="Unique identifier for the email thread")   
                subject: str = Field(..., description="Subject of the email message")
                send_from: str = Field(..., description="Email address sent from")
                content: str = Field(..., description="Body content of the email message")
                action_items: List[str] = Field(..., description="Actionable items extracted from the email")
                answers: List[str] = Field(..., description="Relevant answers to the action items")
        Returns:
            str: A message indicating the result of the draft creation.
            
        The function performs the following steps:
        1. Extracts necessary fields from the input email data, including subject, from_email, content, thread_id, message_id, action_items, and answers.
        2. Authenticates with Gmail using the authenticate_gmail function.
        3. Creates a draft email using the GmailCreateDraft class with the extracted email details.
        4. Returns a message indicating the result of the draft creation.
        """
        email_data = input_data
        print("🔍 Debug: Received data in create_draft tool:\n", email_data)
        
        print(json.dumps(email_data, indent=4))
        logging.debug("🔍 Debug: Received data in create_draft tool:\n", email_data)
     
        # Extract necessary fields
        #subject = email_data.subject
        subject = "placeholder"
        reply_email = email_data.send_from
        #content = email_data.content
        #threadId = email_data.threadId
        #id = email_data.id
        action_items = email_data.action_items
        answers = email_data.answers if email_data.answers else "IDK: Let me get back soon"
        
        #email, subject, message = data.split('|')
        #gmail = GmailToolkit()   # cannot be used directly because assumptions behind credential file location
        #gmail = authenticate_gmail()  # customised Gmail Authentication
        try:
            gmail = authenticate_gmail()  # custom GmailToolkit
        except Exception as e:
            return f"Failed to authenticate Gmail: {e}"
        
        draft = GmailCreateDraft(api_resource=gmail.api_resource)
        draft_payload = {
                "to": [reply_email],
                "subject": subject,
                "message": answers
            }
        
        result = draft.run(draft_payload)
        return f"Draft created: {result}"



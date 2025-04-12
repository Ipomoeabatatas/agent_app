
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


#from crewai_module.schemas import  EmailMessage

from langchain_community.agent_toolkits import GmailToolkit

from msg_app.src.utils.old_load_config import load_config
from msg_app.src.utils.gmail_authenticator import authenticate_gmail


class CreateDraftTool:

    @tool("create_draft")
    def create_draft(data: str = "") -> str:
        """Useful to create an email draft.
        The input should be a JSON-formatted string with the following structure:
        {
            "email": "recipient@example.com",         # Recipient's email address
            "subject": "Your Subject Here",           # Subject of the email
            "message": "The message body",            # Body content of the email
            "bookingRef": "Booking reference number" # Booking reference or "Not Available" if missing
        }
        """
        
        if not data:
            return "Error: No data provided. Please use the format: email|subject|message"
        
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format. Ensure proper structure."

        # Extract and validate fields
        email = data_dict.get("email")
        subject = data_dict.get("subject", "").strip()
        message = data_dict.get("message", "").strip()
  
        try:
            gmail = authenticate_gmail()  # custom GmailToolkit
        except Exception as e:
            return f"Failed to authenticate Gmail: {e}"
        
        draft = GmailCreateDraft(api_resource=gmail.api_resource)
        draft_payload = {
                "to": [email],
                "subject": subject,
                "message": message
            }
        
        result = draft.run(draft_payload)
        return f"Draft created: {result}"



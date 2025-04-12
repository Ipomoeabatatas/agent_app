

from pydantic import BaseModel, Field
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from crewai.tools import BaseTool
from utils.gmail_authenticator import authenticate_gmail

class CreateDraftInput(BaseModel):
    email: str = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Reply Email body content")
    bookingRef: str = Field(..., description="Booking reference number or 'Not Available' if missing")

class CreateDraftTool(BaseTool):
    name: str = "create_draft"
    description: str = "Useful to create an email draft."
    args_schema: type[BaseModel] = CreateDraftInput
    

    def _run(self, email: str, subject: str, message: str, bookingRef: str) -> str :

        # Authenticate Gmail API
        try:
            gmail = authenticate_gmail()  # Ensure this function is correctly implemented
        except Exception as e:
            return f"Failed to authenticate Gmail: {str(e)}"

        # Create draft payload
        draft_payload = {
            "to": [email],
            "subject": bookingRef + " | " + subject,
            "message": message
        }

        # Attempt to create the draft
        try:
            draft = GmailCreateDraft(api_resource=gmail.api_resource)
            result = draft.run(draft_payload)
            return f"Draft created successfully: {result}"
        except Exception as e:
            return f"Error creating draft: {str(e)}"
        

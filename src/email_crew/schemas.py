from pydantic import BaseModel, Field
from typing import List

# Pydantic Model

class ParsedEmail(BaseModel):
    messageId: str = Field(..., description="Unique identifier for the individual message")
    threadId: str = Field(..., description="Unique identifier for the email thread")   
    subject: str = Field(..., description="Subject of the email message")
    bookingRef: str = Field(..., description="booking number is assigned by the carrier when a shipper reserves space on a vessel")
    senderEmail: str = Field(..., description="Email address of sender")
    subject: str = Field(..., description="Subject of the email message")
    content: str = Field(..., description="Body content of the email message")
    actionItems: List[str] = Field(..., description="Actionable items identified from the email")
    answers: List[str] = Field(..., description="answers to the action items")
    
class ParsedEmails(BaseModel):
    emails: List[ParsedEmail] = Field(default_factory=list, description="List of parsed email messages")
    
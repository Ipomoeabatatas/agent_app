# Standard Library Imports
import os
import base64
import pickle
from datetime import datetime

# Third-Party Library Imports
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# application specific imports    
from utils.config_loader import app_config as config
from utils.sanitize_filename import sanitize_filename
from utils.gmail_authenticator import authenticate_gmail


class ExportMailTool:
    def __init__(self):
        self.credentials = config.CREDENTIALS
        self.token = config.TOKEN_PICKLE
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
#       self.service = self._authenticate_gmail(credentials=self.credentials, token_path=self.token)
        self.gmail = authenticate_gmail()
        self.service = self.gmail.api_resource

# the following method is not needed as the authenticate_gmail method is already defined in the authenticate_gmail.py file
# do not remove yet as it is still being used as a reference / backup

    def _authenticate_gmail(self, credentials="credentials.json", token_path="token.pickle"):
        """
        Authenticates and initializes the Gmail API service using OAuth 2.0.
        This function attempts to load saved credentials from a specified token file.
        If no valid credentials are found, it initiates the OAuth 2.0 flow to obtain new credentials.
        The obtained credentials are then saved for future use.
        Args:
            credentials (str): The path to the client secrets JSON file. Default is "credentials.json".
            token_path (str): The path to the token file where credentials are saved. Default is "token.pickle".
        Returns:
            googleapiclient.discovery.Resource: An authorized Gmail API service instance.
        Raises:
            FileNotFoundError: If the credentials file is not found.
            google.auth.exceptions.GoogleAuthError: If there is an error during the authentication process.
        Example:
            service = authenticate_gmail()
        """
        creds = None
    
        # Load saved credentials (if available)
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials exist, start OAuth 2.0 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials, self.SCOPES)
                creds = flow.run_local_server(port=0)  # Opens a browser for authentication

        # Save the credentials for next time
            with open(token_path, "wb") as token_file:
                pickle.dump(creds, token_file)

        # Initialize the Gmail API service
        service = build("gmail", "v1", credentials=creds)
        print("✅ Gmail API authentication successful!")
        return service

    
    def save_email_with_attachments_as_eml(self, service, msg_id, save_path="outputs/ref_number"):
        """
        Fetches an email by ID and saves it as an .eml file, including attachments.

        Args:
        service (googleapiclient.discovery.Resource): The authenticated Gmail API service object.
        msg_id (str): The Gmail message ID of the email to save.
        save_path (str, optional): Directory where the .eml file will be saved. Default is "emails".

        Returns:
        str: The file path of the saved .eml file.
        """
        try:
            # Fetch full email details in "raw" format to preserve attachments
            msg_detail = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()

            # Decode the raw email content from Base64 (full RFC 822 email format)
            if "raw" in msg_detail:
                raw_email = base64.urlsafe_b64decode(msg_detail["raw"]).decode("utf-8")
            else:
                print(f"❌ 'raw' key not found in message details for msg_id: {msg_id}")
                return None

            # Ensure the save directory exists
            os.makedirs(save_path, exist_ok=True)

            # Define file path (using message ID)
            eml_filename = f"email_{msg_id}.eml"
            eml_file_path = os.path.join(save_path, eml_filename)

            # Save as .eml file (which includes attachments)
            with open(eml_file_path, "w", encoding="utf-8") as eml_file:
                eml_file.write(raw_email)

            print(f"📩 Email (with attachments) saved as: {eml_file_path}")
            return eml_file_path
        except Exception as e:
            print(f"❌ Failed to save email as EML: {e}")
            return None
        


################

    def extract_email_body(self, payload):
        """
        Recursively extracts the best available email body (HTML or plain text).
        """
        html_body, plain_text_body = None, None

        if "body" in payload and "data" in payload["body"]:
            content_type = payload.get("mimeType", "")

            if content_type == "text/html":
                return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
            elif content_type == "text/plain":
                return f"<pre>{base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')}</pre>"

        if "parts" in payload:
            for part in payload["parts"]:
                content_type = part.get("mimeType", "")

                if content_type == "text/html":
                    html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                elif content_type == "text/plain":
                    plain_text_body = f"<pre>{base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')}</pre>"

                if "parts" in part:
                    nested_body = self.extract_email_body(part)
                    if nested_body:
                        return nested_body

        return html_body or plain_text_body or "No content available."
                    
                    



    def save_attachment(self, service, msg_id, part, save_path):
        """
        Saves an email attachment from a given message part.

        Args:
            service (googleapiclient.discovery.Resource): The authenticated Gmail API service object.
            msg_id (str): The Gmail message ID of the email containing the attachment.
            part (dict): The part of the email containing the attachment metadata.
            save_path (str): The directory path where the attachment will be saved.

        Returns:
            str: The file path of the saved attachment, or None if the attachment could not be saved.
        """
        try:
            if "filename" in part and part["filename"]:
                filename = sanitize_filename(part["filename"])
                attachment_id = part["body"].get("attachmentId")
                
                if attachment_id:
                    attachment = service.users().messages().attachments().get(
                        userId="me", messageId=msg_id, id=attachment_id
                    ).execute()

                    data = base64.urlsafe_b64decode(attachment["data"])
                    file_path = os.path.join(save_path, filename)

                    with open(file_path, "wb") as f:
                        f.write(data)

                    print(f"📎 Attachment saved: {file_path}")
                    return file_path
        except HttpError as error:
            print(f"❌ Failed to download attachment: {error}")
            return None
        
    
    


    def extract_email_and_attachments(self, service, msg_id, save_path="emails"):
        """
        Extracts an email, saves its headers and body as an HTML archive, and downloads all attachments.

        Args:
            service (googleapiclient.discovery.Resource): The authenticated Gmail API service object.
            msg_id (str): The Gmail message ID of the email to extract.
            save_path (str, optional): Directory where the email and attachments will be saved. Default is "emails".

        Returns:
            dict: A dictionary containing the paths to the saved email HTML file and a list of attachment file paths.
                  Example: {"email_html": "path/to/email.html", "attachments": ["path/to/attachment1", "path/to/attachment2"]}
                  Returns None if an error occurs during extraction.
        """
        try:
            msg_detail = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            headers = msg_detail["payload"]["headers"]

            subject, sender, recipient, date = "No Subject", "Unknown Sender", "Unknown Recipient", "Unknown Date"

            for header in headers:
                if header["name"] == "Subject":
                    subject = header["value"]
                elif header["name"] == "From":
                    sender = header["value"]
                elif header["name"] == "To":
                    recipient = header["value"]
                elif header["name"] == "Date":
                    date = header["value"]

            safe_subject = sanitize_filename(subject)
            #timestamp = datetime.now().strftime("%y%m%d%H%M")
            #email_folder = os.path.join(save_path, f"{timestamp}")
            email_folder = save_path
            os.makedirs(email_folder, exist_ok=True)

            email_body = self.extract_email_body(msg_detail["payload"])

            # Save email as HTML
            email_html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
                    .metadata {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
                    .metadata p {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="metadata">
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>From:</strong> {sender}</p>
                    <p><strong>To:</strong> {recipient}</p>
                    <p><strong>Date:</strong> {date}</p>
                </div>
                <hr>
                <div class="email-body">
                    {email_body}
                </div>
            </body>
            </html>
            """

            email_html_path = os.path.join(email_folder, f"{safe_subject}.html")
            with open(email_html_path, "w", encoding="utf-8") as html_file:
                html_file.write(email_html_content)

            # Process attachments
            attachments = []
            if "parts" in msg_detail["payload"]:
                for part in msg_detail["payload"]["parts"]:
                    attachment_path = self.save_attachment(service, msg_id, part, email_folder)
                    if attachment_path:
                        attachments.append(attachment_path)

            print(f"📧 Email archived: {email_html_path}")
            return {"email_html": email_html_path, "attachments": attachments}

        except Exception as e:
            print(f"❌ Error extracting email: {e}")
            return None



################



if __name__ == "__main__":
    # Initialize the ExportMailTool
    export_tool = ExportMailTool()
    save_path = r"../../../outputs/exports/102030405060"
    
    # Sample JSON data
    data = [
        {
        "id": "1953fc9b25af8bc7",
        "threadId": "1953fc9b25af8bc7",
        "booking_ref": "Not Available",
        "drafts": True,
        "archived": False
        },
        {
        "id": "1953c4c8c4db0fca",
        "threadId": "1953c4c8c4db0fca",
        "booking_ref": "F45451345A",
        "drafts": True,
        "archived": False
        },
        {
        "id": "1953642a8bcb2ca1",
        "threadId": "194f7cca2aae69cc",
        "booking_ref": "Not Available",
        "drafts": True,
        "archived": False
        }
    ]

# ✅ Extract all message IDs into a list
    message_ids = [item["id"] for item in data]

    for test_msg_id in message_ids:
        print(f"Processing message ID: {test_msg_id}")

        print("Export Scenario 1: Save email with attachments as an .eml file")
        # Save the email with attachments as an .eml file
        saved_eml_path = export_tool.save_email_with_attachments_as_eml(
            service=export_tool.service,
            msg_id=test_msg_id,
            save_path=save_path
        )

        if saved_eml_path:
            print(f"Test Success: Email saved successfully at: {saved_eml_path}")
        else:
            print("Test Fail: Failed to save the email.")

        print("Export Scenario 2: Extract email and attachments")
        export_attachments_path = export_tool.extract_email_and_attachments(
            service=export_tool.service,
            msg_id=test_msg_id,
            save_path=save_path
        )
#from langchain.tools import tool
from crewai.tools import tool
from langchain_community.tools.gmail.get_thread import GmailGetThread
from utils.gmail_authenticator import authenticate_gmail

class GetThreadTool:
    @tool("get_thread")
    def get_thread(thread_id: str):
        """
        Useful for retrieving an email threads from Gmail.
        The input should be a valid Gmail thread ID.
        For example, `18923fda12e3a4b1`.
        """
        
        try:
            gmail = authenticate_gmail()  # custom GmailToolkit
        except Exception as e:
            return f"Failed to authenticate Gmail: {e}"
        
        thread_tool = GmailGetThread(api_resource=gmail.api_resource)
        result = thread_tool.run(thread_id)
        
        return f"\nThread details: {result}\n"
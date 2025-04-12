# utils/auth.py

# Standard Library Imports

# Third-Party Library Imports
#from langchain.agents.agent_toolkits import GmailToolkit

from langchain_community.agent_toolkits.gmail.toolkit import GmailToolkit

from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

# Local Application Imports
from utils.config_loader import app_config


def authenticate_gmail()  -> GmailToolkit:
    """
        Authenticates and returns a GmailToolkit instance.
        This function loads the configuration from a TOML file, extracts the necessary
        variables, and uses them to obtain Gmail credentials. It then builds the Gmail
        API resource service and initializes a GmailToolkit instance with it.
        Returns:
            GmailToolkit: An instance of GmailToolkit initialized with the authenticated
                          Gmail API resource service.
    """

 

    TOKEN_PATH = app_config.TOKEN
    CREDENTIALS_PATH = app_config.CREDENTIALS
    SCOPES = app_config.SCOPE
    
    credentials = get_gmail_credentials(
        
        token_file=TOKEN_PATH,
        scopes=SCOPES,
        client_secrets_file=CREDENTIALS_PATH,
    )
    api_resource = build_resource_service(credentials=credentials)
    #print (api_resource) 
    toolkit = GmailToolkit(api_resource=api_resource)
    print (api_resource)
    return toolkit


## DEMO USE
if __name__ == "__main__":
    toolkit = authenticate_gmail()
    print(toolkit.api_resource)
    
    print(toolkit.get_tools)
    toolkit.get_tools()[0]
   
    
    
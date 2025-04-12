from utils.gmail_authenticator import authenticate_gmail
from rag.mail_extractor import ExportMailTool

if __name__ == '__main__':
    print ()
    print ("method 1")
    authenticate_gmail()

    print ("method 2")
    export_mail_tool = ExportMailTool()
#    export_mail_tool._authenticate_gmail()

    print (f"\nYou should see two memory addresses printed above. \nIf you see only one, then the method is not working as expected.")
    print ()


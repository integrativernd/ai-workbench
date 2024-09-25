import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import BASE_DIR, DOCUMENT_ID

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]  # Changed to allow writing

def run_setup():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document and appends a line to it.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    credential_path = os.path.join(BASE_DIR, "google-credentials.json")
    secrets_file_path = os.path.join(BASE_DIR, "credentials.json")
    if os.path.exists(credential_path):
        creds = Credentials.from_authorized_user_file(credential_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_file_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(credential_path, "w") as token:
            token.write(creds.to_json())
    return creds

def append_text(document_id, text):
    creds = run_setup()
    service = build("docs", "v1", credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    
    print(f"The title of the document is: {document.get('title')}")
    
    """Appends text to the end of the document."""
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,  # 1 = end of document
                },
                'text': text + '\n'  # Add a newline for clarity
            }
        }
    ]
    
    result = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()
    return result
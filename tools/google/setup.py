import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import BASE_DIR

# If modifying these scopes, make sure you have the correct permissions on your service account
SCOPES = ["https://www.googleapis.com/auth/documents"]

# The ID of your document
DOCUMENT_ID = "1jHYLQRL0CAolpTHTMm-7Jy-a9XcrZsw868ArZ1IHfHs"

def get_credentials():
    """Gets valid credentials from the service account file."""
    service_account_file = os.path.join(BASE_DIR, "credentials.json")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)
    return credentials

def append_text(service, document_id, text):
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

def run_setup():
    """Updates the document using service account credentials."""
    try:
        credentials = get_credentials()
        service = build("docs", "v1", credentials=credentials)

        # Retrieve the document's contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        print(f"The title of the document is: {document.get('title')}")

        # Append a line to the document
        append_text(service, DOCUMENT_ID, "This is a new line appended to the document.")
        print("A new line has been appended to the document.")

    except HttpError as err:
        print(f"An error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
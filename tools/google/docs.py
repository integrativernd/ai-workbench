import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import BASE_DIR, DOCUMENT_ID, IS_HEROKU_APP, BASE_URL

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]

def get_google_auth_url():
    """
    Generate the Google OAuth 2.0 authorization URL for the web auth flow.
    """
    secrets_file_path = os.path.join(BASE_DIR, "credentials.json")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        secrets_file_path,
        scopes=SCOPES
    )
    flow.redirect_uri = f"{BASE_URL}/auth/google/callback/"
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # Store the state so you can verify it in the callback route
    # You might want to use a session or database to store this securely
    # session['state'] = state
    
    return authorization_url, state

def handle_oauth2_callback(code, state):
    """
    Handle the OAuth 2.0 server's response and obtain credentials.
    """
    # Verify that the state matches the one you stored earlier
    # if state != session['state']:
    #     return None  # Invalid state, potential CSRF attack
    secrets_file_path = os.path.join(BASE_DIR, "credentials.json")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        secrets_file_path,
        scopes=SCOPES,
        state=state
    )

    flow.redirect_uri = f"{BASE_URL}/auth/google/callback/"
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Save the credentials for future use
    credential_path = os.path.join(BASE_DIR, "google-credentials.json")
    with open(credential_path, "w") as token:
        token.write(credentials.to_json())
    
    return credentials

def get_credentials():
    """
    Get valid credentials, either from saved file or through the web auth flow.
    """
    credential_path = os.path.join(BASE_DIR, "google-credentials.json")
    if os.path.exists(credential_path):
        creds = Credentials.from_authorized_user_file(credential_path, SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    
    # If no valid credentials are available, start the web auth flow
    auth_url, state = get_google_auth_url()
    print(f"Please visit this URL to authorize the application: {auth_url}")
    
    # In a web application, you would redirect the user to auth_url here
    # and handle the callback in a separate route
    
    # For demonstration purposes, we'll use input() to simulate the callback
    code = input("Enter the authorization code: ")
    return handle_oauth2_callback(code, state)

def append_text(document_id, text):
    creds = get_credentials()
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
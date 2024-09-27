import os.path

import json
from typing import Dict, List, Any, Callable

# Integrations
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
# from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from llm.anthropic_integration import get_basic_message, anthropic_client

# Configuration
from config.settings import BASE_DIR, DOCUMENT_ID, IS_HEROKU_APP, BASE_URL, SYSTEM_PROMPT

# Models
from tools.models import IntegrationCredential
from django.contrib.auth.models import User


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_google_auth_url():
    """
    Generate the Google OAuth 2.0 authorization URL for the web auth flow.
    """
    secrets_file_path = os.path.join(BASE_DIR, "credentials.json")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        secrets_file_path,
        scopes=SCOPES,
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

def handle_oauth2_callback(request, code, state):
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
    
    # Save the credentials in the database
    IntegrationCredential.objects.update_or_create(
        user=request.user,
        provider='google',
        defaults={'credentials': json.dumps(credentials_to_dict(credentials))}
    )

    return credentials

def get_credentials(provider='google'):
    try:
        user = User.objects.get(username='jtorreggiani')
        credential = IntegrationCredential.objects.get(user=user, provider=provider)
        cred_dict = json.loads(credential.get_credentials())
        return Credentials(
            token=cred_dict['token'],
            refresh_token=cred_dict['refresh_token'],
            token_uri=cred_dict['token_uri'],
            client_id=cred_dict['client_id'],
            client_secret=cred_dict['client_secret'],
            scopes=cred_dict['scopes']
        )
    except IntegrationCredential.DoesNotExist:
        return None
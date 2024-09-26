from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from tools.google.docs import get_google_auth_url, handle_oauth2_callback

def start_google_auth(request):
    authorization_url, state = get_google_auth_url()
    request.session['google_auth_state'] = state
    return redirect(authorization_url)

def google_auth_callback(request):
    state = request.GET.get('state')
    code = request.GET.get('code')

    # import pdb; pdb.set_trace()

    stored_state = request.session.get('google_auth_state')
    if state != stored_state:
        return HttpResponse('Invalid state parameter. Authorization failed.', status=400)
    
    credentials = handle_oauth2_callback(code, state)
    if credentials:
        # Store the credentials in the session or database
        request.session['google_credentials'] = credentials.to_json()
        return redirect('/')  # Redirect to your home page or dashboard
    else:
        return HttpResponse('Failed to obtain credentials.', status=400)
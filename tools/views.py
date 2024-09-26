from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from tools.google.docs import get_google_auth_url, handle_oauth2_callback

def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return staff_member_required(decorated_view_func)

@superuser_required
def start_google_auth(request):
    authorization_url, state = get_google_auth_url()
    request.session['google_auth_state'] = state
    return redirect(authorization_url)

@superuser_required
def google_auth_callback(request):
    state = request.GET.get('state')
    code = request.GET.get('code')
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
from django.shortcuts import render

from django.http import HttpResponse
# from django.views.decorators.http import require_http_methods
from tools.google.docs import run_setup
from django.shortcuts import redirect

# @require_http_methods(["GET"])
def setup_google(request):
    try:
        creds = run_setup()
        # print(f"Auth URL: {auth_url}")
        return redirect("/")
        # return HttpResponse("Document updated successfully", status=200)
        # Redirect to the Google consent page
        # return redirect(auth_url)
    except Exception as e:
        return HttpResponse(f"Error updating document: {str(e)}", status=500)
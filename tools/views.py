from django.shortcuts import render

from django.http import HttpResponse
# from django.views.decorators.http import require_http_methods
from tools.google.docs import run_setup

# @require_http_methods(["GET"])
def setup_google(request):
    try:
        run_setup()
        return HttpResponse("Document updated successfully", status=200)
    except Exception as e:
        return HttpResponse(f"Error updating document: {str(e)}", status=500)
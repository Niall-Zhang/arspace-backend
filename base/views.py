from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import os

def home(request):
    return render(request, "index.html")

def product(request):
    return render(request, "product.html")

def contact(request):
    return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def privacy_policy(request):
    return render(request, "privacy-policy.html")

def privacy_policy_event_holder(request):
    return render(request, "privacy-policy-event-holder.html")

# Apple and android store app redirection view
def platform_redirect(request, param, event_id):
    if 'android' in param:
        return HttpResponseRedirect(os.environ.get("APP_PLAY_STORE_URL"))
    elif 'ios' in param:
        return HttpResponseRedirect(os.environ.get("APP_APPLE_STORE_URL"))
    # Fallback URL or 404
    return HttpResponseRedirect('/')

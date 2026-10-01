from django.shortcuts import render

def home(request):
    """Render the official nexmediaai luxury landing page."""
    return render(request, 'home.html')

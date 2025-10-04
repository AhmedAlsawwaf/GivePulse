from django.shortcuts import render,HttpResponse

def index(request):
    return render(request,"index.html")

def contact(request):
    return render(request, "contact.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def about(request):
    return render(request, "about.html")
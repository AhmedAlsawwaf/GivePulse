from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.contrib import messages
from .forms import LoginForm, DonorRegistrationForm, StaffRegistrationForm
from .models import User,Hospital

def _login(request, user: User):
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

def _logout(request):
    for k in ("user_id", "user_role"):
        request.session.pop(k, None)

def home(request):
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
    return render(request, "home.html", {"user": user})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            _login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    _logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")

def donor_register(request):
    if request.method == "POST":
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user, donor = form.save()
            _login(request, user)
            messages.success(request, "Donor account created.")
            return redirect("dashboard")
    else:
        form = DonorRegistrationForm()
    return render(request, "register_donor.html", {"form": form})

def staff_register(request):
    if request.method == "POST":
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user, staff = form.save()
            _login(request, user)
            messages.success(request, "Staff account created (pending verification).")
            return redirect("dashboard")
    else:
        form = StaffRegistrationForm()
    return render(request, "register_staff.html", {"form": form})

@require_GET
def hospitals_by_city(request):
    city_id = request.GET.get("city_id")
    try:
        city_id = int(city_id)
    except (TypeError, ValueError):
        return JsonResponse({"results": []})

    qs = Hospital.objects.filter(city_id=city_id).order_by("name").values("id", "name")
    return JsonResponse({"results": list(qs)})

def dashboard(request):
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")
    return render(request, "dashboard.html", {"user": user})

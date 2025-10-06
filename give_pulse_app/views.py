from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from .forms import LoginForm, DonorRegistrationForm, StaffRegistrationForm, BloodRequestForm
from .models import User,Hospital

def index(request):
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
    return render(request,"index.html",{"user": user})

def contact(request):
    return render(request, "contact.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def about(request):
    return render(request, "about.html")
def _login(request, user: User):
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

def _logout(request):
    for k in ("user_id", "user_role"):
        request.session.pop(k, None)

# def home(request):
#     user = None
#     if request.session.get("user_id"):
#         try:
#             user = User.objects.get(pk=request.session["user_id"])
#         except User.DoesNotExist:
#             _logout(request)
#     return render(request, "home.html", {"user": user})

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
    return render(request, "login_view.html", {"form": form})

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

def create_blood_request(request: HttpRequest) -> HttpResponse:
    uid = request.session.get("user_id")
    if not uid:
        messages.error(request, "Please log in.")
        return redirect("login")

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        messages.error(request, "Invalid session. Please log in again.")
        return redirect("login")

    if not hasattr(user, "staff"):
        messages.error(request, "Only staff can create blood requests.")
        return redirect("home")

    staff = user.staff
    if not staff.hospital_id:
        messages.error(request, "Your staff profile has no hospital assigned.")
        return redirect("home")

    if request.method == "POST":
        form = BloodRequestForm(request.POST, staff=staff)
        if form.is_valid():
            br = form.save()
            messages.success(request, f"Blood request #{br.pk} created.")
            return redirect("dashboard")
    else:
        form = BloodRequestForm(staff=staff)

    context = {
        "form": form,
        "hospital": staff.hospital,
        "city": staff.hospital.city,
    }
    return render(request, "blood_request_new.html", context)

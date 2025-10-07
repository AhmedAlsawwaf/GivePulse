from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from django.db import models
from functools import wraps
from .forms import LoginForm, DonorRegistrationForm, StaffRegistrationForm, BloodRequestForm
from .models import User, Hospital, BloodRequest, Match

def require_login(view_func):
    """Decorator to handle user authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = None
        if request.session.get("user_id"):
            try:
                user = User.objects.get(pk=request.session["user_id"])
            except User.DoesNotExist:
                _logout(request)
                return redirect("login")
        else:
            return redirect("login")
        
        return view_func(request, user, *args, **kwargs)
    return wrapper

def require_staff(view_func):
    """Decorator to require staff authentication"""
    @wraps(view_func)
    def wrapper(request, user, *args, **kwargs):
        if not hasattr(user, "staff"):
            messages.error(request, "Only staff can access this page.")
            return redirect("index")
        
        staff = user.staff
        if not staff.hospital_id:
            messages.error(request, "Your staff profile has no hospital assigned.")
            return redirect("index")
        
        return view_func(request, user, staff, *args, **kwargs)
    return wrapper

def require_donor(view_func):
    """Decorator to require donor authentication"""
    @wraps(view_func)
    def wrapper(request, user, *args, **kwargs):
        if not hasattr(user, "donor"):
            messages.error(request, "Only donors can access this page.")
            return redirect("index")
        
        return view_func(request, user, *args, **kwargs)
    return wrapper

def contact(request):
    return render(request, "contact.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def about(request):
    return render(request, "about.html")

def logout_view(request):
    if request.method == "POST":
        _logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect("index")
    else:
        # Show logout confirmation page
        return render(request, "logout_confirm.html")
def _login(request, user: User):
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

def _logout(request):
    for k in ("user_id", "user_role"):
        request.session.pop(k, None)

def index(request):
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
    return render(request,"index.html",{"user": user})

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
    if request.method == "POST":
        _logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect("index")
    else:
        # Show logout confirmation page
        return render(request, "logout_confirm.html")

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

@require_login
def dashboard(request, user):
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
        return redirect("index")

    staff = user.staff
    if not staff.hospital_id:
        messages.error(request, "Your staff profile has no hospital assigned.")
        return redirect("index")

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

def _check_blood_type_compatibility(donor_abo, donor_rh, request_abo, request_rh):
    """Check if donor blood type is compatible with request blood type"""
    # ABO compatibility rules (what the donor can donate TO):
    abo_compatible = False
    if donor_abo == 'O':
        abo_compatible = request_abo in ['O', 'A', 'B', 'AB']
    elif donor_abo == 'A':
        abo_compatible = request_abo in ['A', 'AB']
    elif donor_abo == 'B':
        abo_compatible = request_abo in ['B', 'AB']
    elif donor_abo == 'AB':
        abo_compatible = request_abo == 'AB'
    
    # Rh compatibility rules:
    rh_compatible = False
    if donor_rh == '-':
        rh_compatible = request_rh in ['+', '-']  # Rh- can donate to both
    else:  # donor_rh == '+'
        rh_compatible = request_rh == '+'  # Rh+ can only donate to Rh+
    
    return abo_compatible and rh_compatible

@require_login
def blood_requests_list(request, user):
    """List blood requests for donors"""

    # Get open blood requests
    blood_requests = BloodRequest.objects.filter(status="open").select_related(
        'hospital', 'city', 'created_by__user'
    ).order_by('-created_at')

    # Filter by blood type compatibility and city if user is a donor
    if hasattr(user, 'donor'):
        donor = user.donor
        
        # Check if donor is in cooldown period
        if donor.is_in_cooldown():
            from django.utils import timezone
            messages.warning(request, f"You are in a cooldown period until {donor.cooldown_until.strftime('%B %d, %Y at %I:%M %p')}. You cannot match new requests until then.")
            blood_requests = BloodRequest.objects.none()  # Show no requests
        else:
            # Build compatibility query based on medical blood type compatibility rules
            compatibility_conditions = []
            
            # ABO compatibility rules (what the donor can donate TO):
            if donor.abo == 'O':
                compatibility_conditions.append(models.Q(abo__in=['O', 'A', 'B', 'AB']))
            elif donor.abo == 'A':
                compatibility_conditions.append(models.Q(abo__in=['A', 'AB']))
            elif donor.abo == 'B':
                compatibility_conditions.append(models.Q(abo__in=['B', 'AB']))
            elif donor.abo == 'AB':
                compatibility_conditions.append(models.Q(abo='AB'))
            
            # Rh compatibility rules:
            if donor.rh == '-':
                compatibility_conditions.append(models.Q(rh__in=['+', '-']))
            else:  # donor.rh == '+'
                compatibility_conditions.append(models.Q(rh='+'))
            
            # City filtering - donors can only see requests from their city
            city_condition = models.Q(city=donor.city)
            
            # Combine all conditions
            if compatibility_conditions:
                abo_condition = compatibility_conditions[0]
                rh_condition = compatibility_conditions[1]
                compatible_requests = blood_requests.filter(abo_condition & rh_condition & city_condition)
                blood_requests = compatible_requests

    context = {
        "user": user,
        "blood_requests": blood_requests,
    }
    return render(request, "blood_requests_list.html", context)

def blood_request_detail(request, request_id):
    """Show detailed view of a blood request"""
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")

    blood_request = get_object_or_404(BloodRequest, pk=request_id)
    
    # Check if donor has already matched this request
    already_matched = False
    is_compatible = False
    in_cooldown = False
    if hasattr(user, 'donor'):
        already_matched = Match.objects.filter(
            blood_request=blood_request,
            donor=user.donor
        ).exists()
        
        # Check blood type compatibility
        is_compatible = _check_blood_type_compatibility(
            user.donor.abo, user.donor.rh, 
            blood_request.abo, blood_request.rh
        )
        
        # Check if donor is in cooldown period
        in_cooldown = user.donor.is_in_cooldown()

    context = {
        "user": user,
        "blood_request": blood_request,
        "already_matched": already_matched,
        "is_compatible": is_compatible,
        "in_cooldown": in_cooldown,
    }
    return render(request, "blood_request_detail.html", context)

def match_blood_request(request, request_id):
    """Allow donors to match/respond to blood requests"""
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")

    if not hasattr(user, "donor"):
        messages.error(request, "Only donors can match blood requests.")
        return redirect("index")

    blood_request = get_object_or_404(BloodRequest, pk=request_id)
    
    # Check if already matched
    if Match.objects.filter(blood_request=blood_request, donor=user.donor).exists():
        messages.info(request, "You have already matched this blood request.")
        return redirect("blood_request_detail", request_id=request_id)
    
    # Check blood type compatibility
    donor = user.donor
    is_compatible = _check_blood_type_compatibility(donor.abo, donor.rh, blood_request.abo, blood_request.rh)
    
    if not is_compatible:
        messages.error(request, f"Your blood type ({donor.abo}{donor.rh}) is not compatible with this request ({blood_request.abo}{blood_request.rh}).")
        return redirect("blood_request_detail", request_id=request_id)
    
    # Check if donor is in cooldown period
    if donor.is_in_cooldown():
        from django.utils import timezone
        messages.error(request, f"You are in a cooldown period until {donor.cooldown_until.strftime('%B %d, %Y at %I:%M %p')}. You cannot match new requests until then.")
        return redirect("blood_request_detail", request_id=request_id)

    if request.method == "POST":
        # Create match
        match = Match.objects.create(
            blood_request=blood_request,
            donor=user.donor,
            status="pending"
        )
        messages.success(request, f"Match #{match.id} created successfully. Staff will review your match.")
        return redirect("blood_request_detail", request_id=request_id)

    context = {
        "user": user,
        "blood_request": blood_request,
        "is_compatible": is_compatible,
    }
    return render(request, "match_blood_request.html", context)

def accept_match(request, match_id):
    """Accept a donor match"""
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")

    if not hasattr(user, "staff"):
        messages.error(request, "Only staff can accept matches.")
        return redirect("index")

    staff = user.staff
    if not staff.hospital_id:
        messages.error(request, "Your staff profile has no hospital assigned.")
        return redirect("index")

    match = get_object_or_404(Match, pk=match_id, blood_request__hospital=staff.hospital)
    
    if match.status != "pending":
        messages.error(request, "This match is not pending and cannot be accepted.")
        return redirect("manage_matches", request_id=match.blood_request.id)

    from django.utils import timezone
    match.status = "accepted"
    match.accepted_at = timezone.now()
    match.save()

    # Automatically update blood request status based on fulfillment
    blood_request = match.blood_request
    blood_request.units_fulfilled += 1  # Assuming 1 unit per match
    
    # Update request status based on fulfillment level
    if blood_request.units_fulfilled >= blood_request.units_requested:
        blood_request.status = "fulfilled"
    elif blood_request.units_fulfilled > 0:
        blood_request.status = "partial"
    
    blood_request.save()
    
    # Set cooldown period for the donor (8 weeks = 56 days)
    donor = match.donor
    donor.set_cooldown(days=56)

    messages.success(request, f"Match #{match.id} has been accepted. Request status updated to {blood_request.status}. Donor is now in cooldown period.")
    return redirect("manage_matches", request_id=match.blood_request.id)

@require_login
@require_staff
def staff_blood_requests(request, user, staff):
    """Staff view of their hospital's blood requests"""

    # Get all blood requests for this hospital
    blood_requests = BloodRequest.objects.filter(hospital=staff.hospital).select_related(
        'created_by__user', 'city'
    ).order_by('-created_at')

    context = {
        "user": user,
        "blood_requests": blood_requests,
        "hospital": staff.hospital,
    }
    return render(request, "staff_blood_requests.html", context)

def manage_matches(request, request_id):
    """Staff manage matches for a specific blood request"""
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")

    if not hasattr(user, "staff"):
        messages.error(request, "Only staff can manage matches.")
        return redirect("index")

    staff = user.staff
    if not staff.hospital_id:
        messages.error(request, "Your staff profile has no hospital assigned.")
        return redirect("index")

    blood_request = get_object_or_404(BloodRequest, pk=request_id, hospital=staff.hospital)
    matches = Match.objects.filter(blood_request=blood_request).select_related(
        'donor__user'
    ).order_by('-created_at')

    context = {
        "user": user,
        "blood_request": blood_request,
        "matches": matches,
        "hospital": staff.hospital,
    }
    return render(request, "manage_matches.html", context)

@require_login
@require_donor
def donor_matches(request, user):
    """Donor view of their matches"""

    # Get all matches for this donor
    matches = Match.objects.filter(donor=user.donor).select_related(
        'blood_request__hospital', 'blood_request__city'
    ).order_by('-created_at')

    context = {
        "user": user,
        "matches": matches,
    }
    return render(request, "donor_matches.html", context)

def decline_match(request, match_id):
    """Decline a donor match"""
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
            return redirect("login")
    else:
        return redirect("login")

    if not hasattr(user, "staff"):
        messages.error(request, "Only staff can decline matches.")
        return redirect("index")

    staff = user.staff
    if not staff.hospital_id:
        messages.error(request, "Your staff profile has no hospital assigned.")
        return redirect("index")

    match = get_object_or_404(Match, pk=match_id, blood_request__hospital=staff.hospital)
    
    if match.status != "pending":
        messages.error(request, "This match is not pending and cannot be declined.")
        return redirect("manage_matches", request_id=match.blood_request.id)

    from django.utils import timezone
    match.status = "declined"
    match.declined_at = timezone.now()
    match.save()

    messages.success(request, f"Match #{match.id} has been declined.")
    return redirect("manage_matches", request_id=match.blood_request.id)

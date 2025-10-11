from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from django.db import models
from functools import wraps
from .forms import LoginForm, DonorRegistrationForm, StaffRegistrationForm, BloodRequestForm
from .models import ContactMessage, User, Hospital, BloodRequest, Match, DonationAppointment, Donation, SuccessStory
from django.db.models import Count
from .forms import ContactForm
from django.core.mail import send_mail, BadHeaderError


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

def _login(request, user: User):
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

def _logout(request):
    """Logout user and clear session data"""
    for k in ("user_id", "user_role"):
        request.session.pop(k, None)
    
    # Clear the entire session to ensure complete logout
    request.session.flush()


def index(request):
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            _logout(request)
    
    # Get leaderboard data (top 10 donors by donation count)
    # Include both 'completed' and 'donated' statuses for existing data compatibility
    leaderboard_users = User.objects.filter(
        donor__matches__status__in=['completed', 'donated']
    ).annotate(
        donation_count=Count('donor__matches', filter=models.Q(donor__matches__status__in=['completed', 'donated']))
    ).filter(
        donation_count__gt=0
    ).order_by('-donation_count')[:10]
    
    # Format leaderboard data for template
    leaderboard = []
    for rank, leaderboard_user in enumerate(leaderboard_users, 1):
        leaderboard.append({
            'rank': rank,
            'name': f"{leaderboard_user.first_name} {leaderboard_user.last_name}",
            'donation_count': leaderboard_user.donation_count,
            'city': leaderboard_user.donor.city.name if hasattr(leaderboard_user, 'donor') and leaderboard_user.donor.city else 'N/A'
        })
    
    # Get success stories from database (limit to first 4)
    success_stories = SuccessStory.objects.filter(is_published=True).order_by('display_order', '-created_at')[:4]
    
    context = {
        "user": user,
        "leaderboard": leaderboard,
        "success_stories": success_stories
    }
    response = render(request, "index.html", context)
    # Add cache-busting headers to prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

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

    # Get blood requests that still need donations (open or partial)
    blood_requests = BloodRequest.objects.filter(status__in=["open", "partial"]).select_related(
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
    
    # Check if request is still accepting matches (open or partial)
    if blood_request.status not in ["open", "partial"]:
        messages.error(request, f"This blood request is no longer accepting matches (Status: {blood_request.get_status_display()}).")
        return redirect("blood_request_detail", request_id=request_id)
    
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

    # Note: We don't update blood_request status here because the donation hasn't been completed yet
    # The request should remain "open" until the actual donation is completed
    # Status will be updated in the complete_donation view
    
    # Set cooldown period for the donor (8 weeks = 56 days)
    donor = match.donor
    donor.set_cooldown(days=56)

    # Create donation appointment with QR code
    from datetime import timedelta
    appointment_start = timezone.now() + timedelta(hours=24)  # 24 hours from now
    appointment_end = appointment_start + timedelta(hours=2)  # 2-hour window
    
    appointment = DonationAppointment.objects.create(
        match=match,
        window_start=appointment_start,
        window_end=appointment_end
    )
    
    # Generate QR code data
    appointment.qr_code_data = appointment.generate_qr_data()
    appointment.save()
    
    # Generate QR code image
    try:
        import qrcode
        from django.conf import settings
        import os
        
        # Ensure we have QR data
        if not appointment.qr_code_data:
            raise Exception("No QR code data available")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(appointment.qr_code_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_filename = f"qr_appointment_{appointment.id}.png"
        qr_path = os.path.join(settings.MEDIA_ROOT, "qr_codes", qr_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        
        # Save QR code image
        qr_image.save(qr_path)
        
        # Update appointment with QR code image path
        appointment.qr_code_image.name = f"qr_codes/{qr_filename}"
        appointment.save()
        
        # Verify the file was created
        if not os.path.exists(qr_path):
            raise Exception(f"QR code file was not created at {qr_path}")
            
    except ImportError:
        messages.warning(request, "QR code generation failed - qrcode module not available. Appointment created without QR code image.")
    except Exception as e:
        messages.warning(request, f"QR code generation failed: {str(e)}. Appointment created without QR code image.")
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"QR code generation failed for appointment {appointment.id}: {str(e)}")

    messages.success(request, f"Match #{match.id} has been accepted. Donation appointment created with QR code. Donor is now in cooldown period. Request remains open until donation is completed.")
    return redirect("manage_matches", request_id=match.blood_request.id)

def verify_qr_code(request):
    """Verify QR code and show appointment details"""
    if request.method == "POST":
        qr_data = request.POST.get("qr_data")
        
        if qr_data:
            # Clean and validate the QR data
            qr_data = qr_data.strip()
            
            # Check if it looks like our appointment QR code
            if not qr_data.startswith('{'):
                messages.error(request, f"Invalid QR code format. Expected JSON data starting with '{{', but got: {repr(qr_data[:50])}")
                return render(request, "verify_qr.html", {"is_valid": False})
            
            if 'appointment_id' not in qr_data:
                messages.error(request, f"Invalid QR code. This doesn't appear to be a GivePulse appointment QR code. Data: {repr(qr_data[:100])}")
                return render(request, "verify_qr.html", {"is_valid": False})
            
            try:
                import json
                data = json.loads(qr_data)
                
                # Validate required fields
                required_fields = ['appointment_id', 'match_id', 'donor_id']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    messages.error(request, f"Invalid QR code. Missing required fields: {', '.join(missing_fields)}")
                    return render(request, "verify_qr.html", {"is_valid": False})
                
                appointment_id = data.get("appointment_id")
                appointment = get_object_or_404(DonationAppointment, pk=appointment_id)
                
                context = {
                    "appointment": appointment,
                    "qr_data": data,
                    "is_valid": True
                }
                return render(request, "verify_qr.html", context)
                
            except json.JSONDecodeError as e:
                messages.error(request, f"Invalid JSON format in QR code. Error: {str(e)}. Data: {repr(qr_data[:100])}")
                return render(request, "verify_qr.html", {"is_valid": False})
            except DonationAppointment.DoesNotExist as e:
                messages.error(request, f"Appointment not found. Please check the QR code.")
                return render(request, "verify_qr.html", {"is_valid": False})
            except Exception as e:
                messages.error(request, f"Error processing QR code: {str(e)}")
                return render(request, "verify_qr.html", {"is_valid": False})
        else:
            messages.error(request, "No QR code data received.")
            return render(request, "verify_qr.html", {"is_valid": False})
    
    return render(request, "verify_qr.html", {"is_valid": None})

def verify_certificate(request):
    """Verify certificate authenticity using QR code data"""
    if request.method == "POST":
        qr_data = request.POST.get("qr_data")
        if qr_data:
            try:
                import json
                data = json.loads(qr_data)
                
                # Validate required fields
                required_fields = ['certificate_serial', 'donation_id']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    messages.error(request, f"Invalid certificate QR code. Missing required fields: {', '.join(missing_fields)}")
                    return render(request, "verify_certificate.html", {"is_valid": False})
                
                # Get the donation record
                donation = get_object_or_404(Donation, pk=data['donation_id'])
                
                # Verify the certificate serial matches
                if donation.certificate_serial != data['certificate_serial']:
                    messages.error(request, "Certificate serial number mismatch. This certificate may be invalid.")
                    return render(request, "verify_certificate.html", {"is_valid": False})
                
                context = {
                    "donation": donation,
                    "qr_data": data,
                    "is_valid": True
                }
                return render(request, "verify_certificate.html", context)
                
            except json.JSONDecodeError as e:
                messages.error(request, f"Invalid JSON format in QR code. Error: {str(e)}")
                return render(request, "verify_certificate.html", {"is_valid": False})
            except Donation.DoesNotExist:
                messages.error(request, "Certificate not found. This certificate may be invalid or expired.")
                return render(request, "verify_certificate.html", {"is_valid": False})
            except Exception as e:
                messages.error(request, f"Error verifying certificate: {str(e)}")
                return render(request, "verify_certificate.html", {"is_valid": False})
        else:
            messages.error(request, "No QR code data received.")
            return render(request, "verify_certificate.html", {"is_valid": False})
    
    return render(request, "verify_certificate.html", {"is_valid": None})


@require_login
@require_staff
def complete_donation(request, user, staff, appointment_id):
    """Staff marks donation as completed and generates certificate"""
    appointment = get_object_or_404(DonationAppointment, pk=appointment_id)
    
    # Verify the appointment belongs to staff's hospital
    if appointment.match.blood_request.hospital != staff.hospital:
        messages.error(request, "You can only complete donations for your hospital.")
        return redirect("index")
    
    if appointment.match.status != "accepted":
        messages.error(request, "This appointment is not in accepted status.")
        return redirect("index")
    
    # Check if donation already exists for this match
    if hasattr(appointment.match, 'donation'):
        messages.warning(request, "This donation has already been completed.")
        return redirect("manage_matches", request_id=appointment.match.blood_request.id)
    
    if request.method == "POST":
        # Generate certificate serial first
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        certificate_serial = f"GP-{timestamp}-{unique_id}"
        
        # Create donation record with certificate serial
        donation = Donation.objects.create(
            match=appointment.match,
            confirmed_by=staff,
            units=1,  # Default 1 unit, can be made configurable
            certificate_serial=certificate_serial
        )
        
        # Generate certificate
        try:
            donation.generate_certificate()
            messages.success(request, f"Donation completed successfully! Certificate generated with serial: {donation.certificate_serial}")
        except Exception as e:
            messages.error(request, f"Donation completed but certificate generation failed: {str(e)}")
        
        # Update match status
        from django.utils import timezone
        appointment.match.status = "donated"
        appointment.match.donated_at = timezone.now()
        appointment.match.save()
        
        # Update blood request status based on actual donation completion
        blood_request = appointment.match.blood_request
        blood_request.units_fulfilled += donation.units
        
        # Update request status based on fulfillment level
        if blood_request.units_fulfilled >= blood_request.units_requested:
            blood_request.status = "fulfilled"
        elif blood_request.units_fulfilled > 0:
            blood_request.status = "partial"
        
        blood_request.save()
        
        return redirect("staff_blood_requests")
    
    context = {
        "appointment": appointment,
        "donor": appointment.match.donor,
        "blood_request": appointment.match.blood_request
    }
    return render(request, "complete_donation.html", context)

@require_login
@require_donor
def donor_appointments(request, user):
    """Donor view of their appointments"""
    donor = user.donor
    from django.db import models
    appointments = DonationAppointment.objects.filter(
        match__donor=donor,
        match__status__in=["accepted", "checked_in", "donated"]
    ).filter(
        models.Q(qr_code_data__isnull=False) & ~models.Q(qr_code_data='')  # Only show appointments with valid QR data
    ).order_by("-created_at")
    
    context = {
        "appointments": appointments
    }
    return render(request, "donor_appointments.html", context)

@require_login
@require_donor
def donor_donations(request, user):
    """Donor view of their donation history"""
    donor = user.donor
    donations = Donation.objects.filter(
        match__donor=donor
    ).order_by("-confirmed_at")
    
    context = {
        "donations": donations
    }
    return render(request, "donor_donations.html", context)

def download_certificate(request, donation_id):
    """Download donation certificate"""
    donation = get_object_or_404(Donation, pk=donation_id)
    
    # Check if user is the donor or staff from the same hospital
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            pass
    
    if not user:
        messages.error(request, "You must be logged in to download certificates.")
        return redirect("login")
    
    # Check permissions
    can_download = False
    if hasattr(user, "donor") and donation.match.donor == user.donor:
        can_download = True
    elif hasattr(user, "staff") and donation.match.blood_request.hospital == user.staff.hospital:
        can_download = True
    
    if not can_download:
        messages.error(request, "You don't have permission to download this certificate.")
        return redirect("index")
    
    if not donation.certificate_file:
        messages.error(request, "Certificate not found.")
        return redirect("index")
    
    from django.http import FileResponse
    import os
    from django.conf import settings
    
    file_path = os.path.join(settings.MEDIA_ROOT, donation.certificate_file.name)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"donation_certificate_{donation.certificate_serial}.pdf")
    else:
        messages.error(request, "Certificate file not found.")
        return redirect("index")

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


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            ContactMessage.objects.create(name=name, email=email, message=message)

            subject = f"📩 New Message from {name}"
            body = f"From: {name} <{email}>\n\nMessage:\n{message}"

            try:
                send_mail(subject, body, email, ["givepulse25@gmail.com"])
                messages.success(request, "✅ Your message has been sent successfully!")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.error(request, f"⚠️ Error sending email: {e}")

            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})
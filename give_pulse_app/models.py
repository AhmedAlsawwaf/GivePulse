from __future__ import annotations
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .validators import validate_person_name, validate_phone, validate_profile_image
from .uploads import donor_avatar_path
from .managers import UserManager, StaffManager, DonorManager,BloodRequestManager
# Choices :
class Role(models.TextChoices):
    GUEST = "guest", "Guest"
    DONOR = "donor", "Donor"
    STAFF = "staff", "Staff"
    ADMIN = "admin", "Admin"

class BloodType(models.TextChoices):
    O = "O", "O"
    A = "A", "A"
    B = "B", "B"
    AB = "AB", "AB"

class RhType(models.TextChoices):
    POS = "+", "Rh+"
    NEG = "-", "Rh-"

class RequestStatus(models.TextChoices):
    OPEN = "open", "Open"
    PARTIAL = "partial", "Partial"
    FULFILLED = "fulfilled", "Fulfilled"
    EXPIRED = "expired", "Expired"

class MatchStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    CHECKED_IN = "checked_in", "Checked-in"
    DONATED = "donated", "Donated"

# Models
class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, related_name="cities",null=True,blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["governorate"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.governorate})"
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="hospitals")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("name", "city")]
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["is_verified"]),
        ]
    def __str__(self):
        return f"{self.name} ({self.city})"

class User(models.Model):
    first_name = models.CharField(max_length=150, validators=[validate_person_name])
    last_name = models.CharField(max_length=150, validators=[validate_person_name])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone])
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    
    # Required Django User model attributes
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_staff(self):
        return self.role == 'admin'
    
    @property
    def is_superuser(self):
        return self.role == 'admin'
    
    def natural_key(self):
        """Required for Django admin interface"""
        return (self.email,)
    
    def set_password(self, raw_password):
        """Required for Django admin interface"""
        from .managers import _hash_password_if_needed
        self.password = _hash_password_if_needed(raw_password)
        # Only save if the user already has a primary key (is saved)
        if self.pk:
            self.save(update_fields=['password', 'updated_at'])
    
    def check_password(self, raw_password):
        """Required for Django admin interface"""
        from .managers import check_password
        return check_password(raw_password, self.password)
    
    def has_perm(self, perm, obj=None):
        return self.role == 'admin'
    
    def has_module_perms(self, app_label):
        return self.role == 'admin'

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="staff")
    role = models.CharField(max_length=50, default="staff")  
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = StaffManager()

    class Meta:
        indexes = [
            models.Index(fields=["hospital", "is_verified"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.hospital}"

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="donor")
    profile_picture = models.ImageField(
        upload_to=donor_avatar_path, 
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),validate_profile_image,],
        help_text="JPEG/PNG/WEBP, ≤2MB"
    )
    abo = models.CharField(max_length=2, choices=BloodType.choices)
    rh = models.CharField(max_length=1, choices=RhType.choices)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="donors")
    last_donation = models.DateField(null=True, blank=True)
    cooldown_until = models.DateTimeField(null=True, blank=True, help_text="Donor cannot match until this date")
    eligibility_consent = models.BooleanField(default=False)
    public_alias = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = DonorManager()
    
    def save(self, *args, **kwargs):
        try:
            old = type(self).objects.get(pk=self.pk)
        except type(self).DoesNotExist:
            old = None
        super().save(*args, **kwargs)
        if old and old.profile_picture and old.profile_picture != self.profile_picture:
            old.profile_picture.delete(save=False)
    
    def delete(self, *args, **kwargs):
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        super().delete(*args, **kwargs)
    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["abo", "rh"]),
        ]

    def is_in_cooldown(self):
        """Check if donor is in cooldown period"""
        if not self.cooldown_until:
            return False
        from django.utils import timezone
        return timezone.now() < self.cooldown_until
    
    def can_donate(self):
        """Check if donor can donate (not in cooldown)"""
        return not self.is_in_cooldown()
    
    def set_cooldown(self, days=56):
        """Set cooldown period for donor"""
        from django.utils import timezone
        from datetime import timedelta
        self.cooldown_until = timezone.now() + timedelta(days=days)
        self.save(update_fields=['cooldown_until'])

    def __str__(self):
        return f"{self.user} ({self.abo}{self.rh})"


class BloodRequest(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="blood_requests")
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="created_blood_requests")
    units_requested = models.PositiveIntegerField()
    units_fulfilled = models.PositiveIntegerField(default=0)
    abo = models.CharField(max_length=2, choices=BloodType.choices)
    rh = models.CharField(max_length=1, choices=RhType.choices)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="blood_requests")
    deadline_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=RequestStatus.choices, default=RequestStatus.OPEN)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BloodRequestManager()

    def clean(self):
        super().clean()
        if self.hospital_id and self.city_id and self.hospital.city_id != self.city_id:
            raise ValidationError({"city": "City must match the hospital's city."})
    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["deadline_at"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return f"Request #{self.pk} {self.abo}{self.rh} x{self.units_requested}"
    
class Match(models.Model):
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name="matches")
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="matches")
    status = models.CharField(max_length=12, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    notified_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    donated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("blood_request", "donor")]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Match #{self.pk}"

class DonationAppointment(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="appointment")
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    qr_code_data = models.TextField(blank=True, help_text="QR code data for verification")
    qr_code_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        super().clean()
        if self.window_end <= self.window_start:
            raise ValidationError({"window_end": "End must be after start."})
    
    def generate_qr_data(self):
        """Generate QR code data with appointment information"""
        from django.utils import timezone
        data = {
            "appointment_id": self.id,
            "match_id": self.match.id,
            "donor_id": self.match.donor.id,
            "donor_name": f"{self.match.donor.user.first_name} {self.match.donor.user.last_name}",
            "blood_type": f"{self.match.donor.abo}{self.match.donor.rh}",
            "hospital": self.match.blood_request.hospital.name,
            "appointment_date": self.window_start.isoformat(),
            "verification_code": f"GP{self.id:06d}{self.match.id:06d}",
            "created_at": timezone.now().isoformat()
        }
        import json
        return json.dumps(data)
    
    def __str__(self):
        return f"Appointment for match {self.match_id}"


class Donation(models.Model):
    match = models.OneToOneField(Match, on_delete=models.PROTECT, related_name="donation")
    confirmed_by = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL)
    units = models.PositiveIntegerField(default=1)
    certificate_file = models.FileField(upload_to="certificates/", blank=True)
    certificate_serial = models.CharField(max_length=40, blank=True, unique=True)
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["confirmed_at"]),
        ]

    def generate_certificate_serial(self):
        """Generate unique certificate serial number"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"GP-{timestamp}-{unique_id}"
    
    def generate_certificate(self):
        """Generate enhanced PDF certificate for the donation"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing, Rect
            from reportlab.graphics import renderPDF
            from django.conf import settings
            import os
            import qrcode
            import io
        except ImportError:
            raise Exception("ReportLab or qrcode module not available. Cannot generate certificate.")
        
        if not self.certificate_serial:
            self.certificate_serial = self.generate_certificate_serial()
            self.save(update_fields=['certificate_serial'])
        
        # Create certificate file path
        filename = f"certificate_{self.certificate_serial}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, "certificates", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create PDF with margins
        doc = SimpleDocTemplate(filepath, pagesize=letter, 
                              leftMargin=0.5*inch, rightMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Add decorative border using simple lines
        story.append(Spacer(1, 20))
        
        # Header with logo area
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            alignment=1,  # Center
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"{self.match.blood_request.hospital.name}", header_style))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkblue,
            fontName='Helvetica-Oblique'
        )
        story.append(Paragraph("Blood Donation Service", subtitle_style))
        
        # Main title with decorative line
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=32,
            spaceAfter=40,
            alignment=1,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("CERTIFICATE OF APPRECIATION", title_style))
        
        # Decorative line
        line_style = ParagraphStyle(
            'Line',
            parent=styles['Normal'],
            fontSize=20,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkred
        )
        story.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", line_style))
        
        # Certificate content
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=15,
            alignment=1,
            fontName='Helvetica'
        )
        
        story.append(Paragraph("This is to certify that", content_style))
        story.append(Spacer(1, 15))
        
        # Donor name with special styling
        donor_name = f"{self.match.donor.user.first_name} {self.match.donor.user.last_name}"
        name_style = ParagraphStyle(
            'DonorName',
            parent=styles['Heading2'],
            fontSize=24,
            spaceAfter=25,
            alignment=1,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(donor_name, name_style))
        
        story.append(Paragraph("has successfully donated blood and contributed to saving lives", content_style))
        story.append(Spacer(1, 20))
        
        # Create a table for donation details
        details_data = [
            ['Blood Type:', f"{self.match.donor.abo}{self.match.donor.rh}"],
            ['Units Donated:', f"{self.units} unit(s)"],
            ['Hospital:', f"{self.match.blood_request.hospital.name}"],
            ['Donation Date:', f"{self.confirmed_at.strftime('%B %d, %Y')}"],
            ['Certificate Serial:', f"{self.certificate_serial}"]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 30))
        
        # Generate QR code for verification
        qr_data = {
            "certificate_serial": self.certificate_serial,
            "donor_id": self.match.donor.id,
            "donation_id": self.id,
            "hospital": self.match.blood_request.hospital.name,
            "date": self.confirmed_at.isoformat(),
            "verification_url": f"https://givepulse.com/verify/{self.certificate_serial}"
        }
        
        import json
        qr_json = json.dumps(qr_data)
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        # Save QR code to temporary file
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_temp_path = os.path.join(settings.MEDIA_ROOT, "temp", f"qr_{self.certificate_serial}.png")
        os.makedirs(os.path.dirname(qr_temp_path), exist_ok=True)
        qr_img.save(qr_temp_path)
        
        # Add QR code to PDF
        qr_image = Image(qr_temp_path, width=1.5*inch, height=1.5*inch)
        story.append(qr_image)
        
        # QR code label
        qr_label_style = ParagraphStyle(
            'QRLabel',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=1,
            textColor=colors.grey,
            fontName='Helvetica'
        )
        story.append(Paragraph("Scan QR code to verify certificate authenticity", qr_label_style))
        
        story.append(Spacer(1, 25))
        
        # Appreciation message
        appreciation_style = ParagraphStyle(
            'Appreciation',
            parent=styles['Normal'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("Thank you for your life-saving contribution!", appreciation_style))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=1,
            textColor=colors.darkgrey,
            fontName='Helvetica'
        )
        story.append(Paragraph("GivePulse Blood Donation Management System", footer_style))
        story.append(Paragraph("Gaza City General Hospital • Blood Bank Department", footer_style))
        
        # Signature area
        story.append(Spacer(1, 40))
        signature_data = [
            ['', ''],
            ['_________________________', '_________________________'],
            ['Medical Director', 'Blood Bank Supervisor'],
            ['Dr. Ahmed Al-Masri', 'Dr. Fatima Hassan'],
            ['Date: _______________', 'Date: _______________']
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(signature_table)
        
        # Build PDF
        doc.build(story)
        
        # Clean up temporary QR file
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)
        
        # Save file path to model
        self.certificate_file.name = f"certificates/{filename}"
        self.save(update_fields=['certificate_file'])
        
        return filepath

    def __str__(self):
        return f"Donation for match {self.match_id}"


class SuccessStory(models.Model):
    """Model to store success stories for the home page"""
    title = models.CharField(max_length=200, help_text="Story title (e.g., 'Ahmed's Story')")
    donor_name = models.CharField(max_length=100, help_text="Name of the person in the story")
    story_text = models.TextField(help_text="The success story content")
    image_url = models.URLField(blank=True, help_text="URL for the story image (optional)")
    is_published = models.BooleanField(default=True, help_text="Whether this story should be displayed")
    display_order = models.PositiveIntegerField(default=0, help_text="Order for displaying stories (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return f"{self.title} - {self.donor_name}"

 
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"

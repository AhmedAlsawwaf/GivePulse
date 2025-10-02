from __future__ import annotations
from django.db import models

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
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
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
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="staff")
    role = models.CharField(max_length=50, default="staff")  
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["hospital", "is_verified"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.hospital}"

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="donor")
    abo = models.CharField(max_length=2, choices=BloodType.choices)
    rh = models.CharField(max_length=1, choices=RhType.choices)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    last_donation = models.DateField(null=True, blank=True)
    eligibility_consent = models.BooleanField(default=False)
    public_alias = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["abo", "rh"]),
        ]

    def __str__(self):
        return f"{self.user} ({self.abo}{self.rh})"


class BloodRequest(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="blood_requests")
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="created_blood_requests")
    units_requested = models.PositiveIntegerField()
    units_fulfilled = models.PositiveIntegerField(default=0)
    abo = models.CharField(max_length=2, choices=BloodType.choices)
    rh = models.CharField(max_length=1, choices=RhType.choices)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    deadline_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=RequestStatus.choices, default=RequestStatus.OPEN)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for match {self.match_id}"


class Donation(models.Model):
    match = models.OneToOneField(Match, on_delete=models.PROTECT, related_name="donation")
    confirmed_by = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL)
    units = models.PositiveIntegerField(default=1)
    certificate_file = models.FileField(upload_to="certificates/", blank=True)
    certificate_serial = models.CharField(max_length=40, blank=True)
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["confirmed_at"]),
        ]

    def __str__(self):
        return f"Donation for match {self.match_id}"

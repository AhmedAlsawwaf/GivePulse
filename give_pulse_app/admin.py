from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.db.models import Count
from .models import (
    Governorate, City, Hospital, User, Staff, Donor, BloodRequest, 
    Match, DonationAppointment, Donation, SuccessStory, ContactMessage
)

# Custom Admin Site Configuration
admin.site.site_header = "GivePulse Admin"
admin.site.site_title = "GivePulse Admin"
admin.site.index_title = "Blood Donation Management System"


# Override the admin index view to include dashboard statistics
original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    """Custom admin index with dashboard statistics"""
    extra_context = extra_context or {}
    
    # Get statistics
    total_hospitals = Hospital.objects.count()
    verified_hospitals = Hospital.objects.filter(is_verified=True).count()
    unverified_hospitals = total_hospitals - verified_hospitals
    
    total_staff = Staff.objects.count()
    verified_staff = Staff.objects.filter(is_verified=True).count()
    unverified_staff = total_staff - verified_staff
    
    total_donors = Donor.objects.count()
    total_requests = BloodRequest.objects.count()
    total_donations = Donation.objects.count()
    total_lives_saved = total_donations  # Each donation saves one life
    
    # Add statistics to context
    extra_context.update({
        'total_hospitals': total_hospitals,
        'verified_hospitals': verified_hospitals,
        'unverified_hospitals': unverified_hospitals,
        'total_staff': total_staff,
        'verified_staff': verified_staff,
        'unverified_staff': unverified_staff,
        'total_donors': total_donors,
        'total_requests': total_requests,
        'total_donations': total_donations,
        'total_lives_saved': total_lives_saved,
    })
    
    return original_index(request, extra_context)

# Replace the admin index view
admin.site.index = custom_admin_index

# Governorate Admin
@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ['name', 'city_count']
    search_fields = ['name']
    ordering = ['name']
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = 'Cities Count'

# City Admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'governorate', 'hospital_count', 'donor_count']
    list_filter = ['governorate']
    search_fields = ['name', 'governorate__name']
    ordering = ['governorate__name', 'name']
    
    def hospital_count(self, obj):
        return obj.hospitals.count()
    hospital_count.short_description = 'Hospitals'
    
    def donor_count(self, obj):
        return obj.donors.count()
    donor_count.short_description = 'Donors'

# Hospital Admin
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'verification_status', 'staff_count', 'request_count', 'created_at']
    list_filter = ['is_verified', 'city__governorate', 'created_at']
    search_fields = ['name', 'city__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Hospital Information', {
            'fields': ('name', 'city')
        }),
        ('Verification', {
            'fields': ('is_verified',),
            'description': 'Only verified hospitals can create blood requests'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span class="verification-badge verified">Verified</span>')
        else:
            return format_html('<span class="verification-badge pending">Pending</span>')
    verification_status.short_description = 'Status'
    
    def staff_count(self, obj):
        return obj.staff.count()
    staff_count.short_description = 'Staff'
    
    def request_count(self, obj):
        return obj.blood_requests.count()
    request_count.short_description = 'Requests'
    
    actions = ['verify_hospitals', 'unverify_hospitals']
    
    def verify_hospitals(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} hospitals have been verified.')
    verify_hospitals.short_description = "Verify selected hospitals"
    
    def unverify_hospitals(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} hospitals have been unverified.')
    unverify_hospitals.short_description = "Unverify selected hospitals"

# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Account Settings', {
            'fields': ('role', 'password')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'

# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'hospital', 'verification_status', 'request_count', 'created_at']
    list_filter = ['is_verified', 'hospital__city__governorate', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'hospital__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('user', 'hospital', 'role')
        }),
        ('Verification', {
            'fields': ('is_verified',),
            'description': 'Only verified staff can create and manage blood requests'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = 'Staff Member'
    
    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span class="badge bg-success">Verified</span>')
        else:
            return format_html('<span class="badge bg-warning text-dark">Pending</span>')
    verification_status.short_description = 'Status'
    
    def request_count(self, obj):
        return obj.created_blood_requests.count()
    request_count.short_description = 'Requests Created'
    
    actions = ['verify_staff', 'unverify_staff']
    
    def verify_staff(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} staff members have been verified.')
    verify_staff.short_description = "Verify selected staff"
    
    def unverify_staff(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} staff members have been unverified.')
    unverify_staff.short_description = "Unverify selected staff"

# Donor Admin
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'blood_type', 'city', 'cooldown_status', 'donation_count', 'created_at']
    list_filter = ['abo', 'rh', 'city__governorate', 'eligibility_consent', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'city__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'profile_picture', 'public_alias')
        }),
        ('Blood Information', {
            'fields': ('abo', 'rh', 'city')
        }),
        ('Donation History', {
            'fields': ('last_donation', 'cooldown_until')
        }),
        ('Settings', {
            'fields': ('eligibility_consent',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = 'Donor'
    
    def blood_type(self, obj):
        return f"{obj.abo}{obj.rh}"
    blood_type.short_description = 'Blood Type'
    
    def cooldown_status(self, obj):
        if obj.is_in_cooldown():
            return format_html('<span class="verification-badge pending">In Cooldown</span>')
        else:
            return format_html('<span class="verification-badge verified">Available</span>')
    cooldown_status.short_description = 'Status'
    
    def donation_count(self, obj):
        return obj.matches.filter(status='donated').count()
    donation_count.short_description = 'Donations'

# Blood Request Admin
@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'hospital', 'blood_type', 'units_info', 'status', 'deadline', 'created_by_staff', 'created_at']
    list_filter = ['status', 'abo', 'rh', 'hospital__city__governorate', 'created_at']
    search_fields = ['hospital__name', 'created_by__user__first_name', 'created_by__user__last_name', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('hospital', 'created_by', 'units_requested', 'units_fulfilled')
        }),
        ('Blood Requirements', {
            'fields': ('abo', 'rh', 'city')
        }),
        ('Timeline', {
            'fields': ('deadline_at', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def request_id(self, obj):
        return f"#{obj.pk}"
    request_id.short_description = 'ID'
    
    def blood_type(self, obj):
        return f"{obj.abo}{obj.rh}"
    blood_type.short_description = 'Blood Type'
    
    def units_info(self, obj):
        return f"{obj.units_fulfilled}/{obj.units_requested}"
    units_info.short_description = 'Units'
    
    def deadline(self, obj):
        from django.utils import timezone
        if obj.deadline_at < timezone.now():
            return format_html('<span style="color: red;">{}</span>', obj.deadline_at.strftime('%Y-%m-%d %H:%M'))
        return obj.deadline_at.strftime('%Y-%m-%d %H:%M')
    deadline.short_description = 'Deadline'
    
    def created_by_staff(self, obj):
        return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"
    created_by_staff.short_description = 'Created By'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show requests from verified staff and hospitals
        return qs.filter(
            created_by__is_verified=True,
            hospital__is_verified=True
        )

# Match Admin
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'blood_request', 'donor_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['blood_request__hospital__name', 'donor__user__first_name', 'donor__user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def match_id(self, obj):
        return f"#{obj.pk}"
    match_id.short_description = 'ID'
    
    def donor_name(self, obj):
        return f"{obj.donor.user.first_name} {obj.donor.user.last_name}"
    donor_name.short_description = 'Donor'

# Donation Appointment Admin
@admin.register(DonationAppointment)
class DonationAppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'match', 'window_start', 'window_end', 'qr_code_status']
    list_filter = ['created_at']
    search_fields = ['match__donor__user__first_name', 'match__donor__user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def appointment_id(self, obj):
        return f"#{obj.pk}"
    appointment_id.short_description = 'ID'
    
    def qr_code_status(self, obj):
        if obj.qr_code_image:
            return format_html('<span class="verification-badge verified">Generated</span>')
        else:
            return format_html('<span class="verification-badge pending">Pending</span>')
    qr_code_status.short_description = 'QR Code'

# Donation Admin
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donation_id', 'match', 'units', 'confirmed_by_staff', 'certificate_status', 'confirmed_at']
    list_filter = ['confirmed_at']
    search_fields = ['match__donor__user__first_name', 'match__donor__user__last_name', 'certificate_serial']
    ordering = ['-confirmed_at']
    readonly_fields = ['confirmed_at']
    
    def donation_id(self, obj):
        return f"#{obj.pk}"
    donation_id.short_description = 'ID'
    
    def confirmed_by_staff(self, obj):
        if obj.confirmed_by:
            return f"{obj.confirmed_by.user.first_name} {obj.confirmed_by.user.last_name}"
        return "System"
    confirmed_by_staff.short_description = 'Confirmed By'
    
    def certificate_status(self, obj):
        if obj.certificate_file:
            return format_html('<span class="verification-badge verified">Generated</span>')
        else:
            return format_html('<span class="verification-badge pending">Pending</span>')
    certificate_status.short_description = 'Certificate'

# Success Story Admin
@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor_name', 'is_published', 'display_order', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'donor_name', 'story_text']
    list_editable = ['is_published', 'display_order']
    ordering = ['display_order', '-created_at']

    fieldsets = (
        ('Story Information', {
            'fields': ('title', 'donor_name', 'story_text')
        }),
        ('Display Settings', {
            'fields': ('is_published', 'display_order', 'image_url')
        }),
    )

# Contact Message Admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def has_add_permission(self, request):
        return False  # Contact messages are only created through the contact form

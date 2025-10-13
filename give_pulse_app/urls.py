from django.urls import path
from django.shortcuts import render
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("register/donor/", views.donor_register, name="register_donor"),
    path("register/staff/", views.staff_register, name="register_staff"),
    path("hospitals/", views.hospitals_by_city, name="api_hospitals_by_city"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    
    path("requests/new/", views.create_blood_request, name="blood_request_new"),
    path("requests/", views.blood_requests_list, name="blood_requests_list"),
    path("requests/<int:request_id>/", views.blood_request_detail, name="blood_request_detail"),
    path("requests/<int:request_id>/match/", views.match_blood_request, name="match_blood_request"),
    path("requests/<int:request_id>/match-ajax/", views.match_blood_request_ajax, name="match_blood_request_ajax"),
    path("matches/<int:match_id>/accept/", views.accept_match, name="accept_match"),
    path("matches/<int:match_id>/decline/", views.decline_match, name="decline_match"),
    
    # Staff management
    path("staff/requests/", views.staff_blood_requests, name="staff_blood_requests"),
    path("requests/<int:request_id>/manage/", views.manage_matches, name="manage_matches"),
    
    # Donor management
    path("donor/matches/", views.donor_matches, name="donor_matches"),
    path("donor/appointments/", views.donor_appointments, name="donor_appointments"),
    path("donor/donations/", views.donor_donations, name="donor_donations"),
    
    # QR Code and Donation Management
    path("verify-qr/", views.verify_qr_code, name="verify_qr"),
    path("verify-certificate/", views.verify_certificate, name="verify_certificate"),
    path("complete-donation/<int:appointment_id>/", views.complete_donation, name="complete_donation"),
    path("download-certificate/<int:donation_id>/", views.download_certificate, name="download_certificate"),
    
]

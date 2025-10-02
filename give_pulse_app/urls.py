from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("register/donor/", views.donor_register, name="register_donor"),
    path("register/staff/", views.staff_register, name="register_staff"),
    path("hospitals/", views.hospitals_by_city, name="api_hospitals_by_city"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    
    path("requests/new/", views.create_blood_request, name="blood_request_new"),
]

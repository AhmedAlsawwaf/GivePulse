from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from .models import User, Donor, Staff, City, Hospital, BloodType, RhType
from .validators import validate_password_strength

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    _user = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        if email and password:
            user = User.objects.authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password.")
            self._user = user
        return cleaned

    def get_user(self) -> User | None:
        return self._user


class DonorRegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=150, label="First name")
    last_name  = forms.CharField(max_length=150, label="Last name")
    email      = forms.EmailField(label="Email")
    phone      = forms.CharField(max_length=20, required=False, label="Phone")

    password1  = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2  = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    # Donor fields
    abo  = forms.ChoiceField(choices=BloodType.choices, label="ABO")
    rh   = forms.ChoiceField(choices=RhType.choices, label="Rh")
    city = forms.ModelChoiceField(queryset=City.objects.all(), label="City")

    eligibility_consent = forms.BooleanField(
        required=False,
        label="I consent and confirm I meet eligibility rules",
    )

    profile_picture = forms.ImageField(required=False, label="Profile picture")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()

        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        if p1 != p2:
            raise ValidationError({"password2": "Passwords do not match."})
        validate_password_strength(p1)

        return cleaned

    def save(self):
        cd = self.cleaned_data

        # Uses imported User model (must be imported as shown above)
        user = User.objects.create_user(
            first_name=cd["first_name"],
            last_name=cd["last_name"],
            email=cd["email"],
            password=cd["password1"],   # raw password; manager will hash
            phone=cd.get("phone") or "",
            role="donor",
        )

        # Uses imported Donor model (must be imported as shown above)
        donor = Donor.objects.create_donor(
            user_id=user.id,
            abo=cd["abo"],
            rh=cd["rh"],
            city_id=cd["city"].id,
            eligibility_consent=cd.get("eligibility_consent", False),
        )

        pic = cd.get("profile_picture")
        if pic:
            donor.profile_picture = pic
            donor.full_clean()
            donor.save(update_fields=["profile_picture"])

        return user, donor


class StaffRegistrationForm(forms.Form):
    # User fields
    first_name = forms.CharField(max_length=150, label="First name")
    last_name  = forms.CharField(max_length=150, label="Last name")
    email      = forms.EmailField(label="Email")
    phone      = forms.CharField(max_length=20, required=False, label="Phone")

    password1  = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2  = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    # Dependent selects
    city     = forms.ModelChoiceField(queryset=City.objects.all(), label="City", required=True)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.none(), label="Hospital", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If the user is POSTing a chosen city, pre-filter so the posted hospital choice validates
        data_city = None
        if "city" in self.data:
            try:
                data_city = int(self.data.get("city"))
            except (TypeError, ValueError):
                data_city = None

        if data_city:
            self.fields["hospital"].queryset = Hospital.objects.filter(city_id=data_city).order_by("name")
        else:
            self.fields["hospital"].queryset = Hospital.objects.none()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        if p1 != p2:
            raise ValidationError({"password2": "Passwords do not match."})
        validate_password_strength(p1)

        # Cross-check: hospital belongs to city
        city = cleaned.get("city")
        hospital = cleaned.get("hospital")
        if city and hospital and hospital.city_id != city.id:
            raise ValidationError({"hospital": "Selected hospital does not belong to the chosen city."})

        return cleaned

    def save(self):
        cd = self.cleaned_data
        user = User.objects.create_user(
            first_name=cd["first_name"],
            last_name=cd["last_name"],
            email=cd["email"],
            password=cd["password1"],
            phone=cd.get("phone") or "",
            role="staff",
        )
        staff = Staff.objects.create_staff(
            user_id=user.id,
            hospital_id=cd["hospital"].id,
            role="staff",
            is_verified=False,
        )
        return user, staff
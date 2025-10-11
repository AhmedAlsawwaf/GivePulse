from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User, Donor, Staff, City, Hospital, BloodType, RhType, BloodRequest
from .validators import validate_password_strength


class LoginForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg shadow-sm",
                "placeholder": "Enter your email",
                "autocomplete": "email",
                "id": "id_email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg shadow-sm",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
                "id": "id_password",
            }
        ),
    )

    _user = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        if email and password:
            user = User.objects.authenticate(email=email, password=password)
            if not user:
                self.add_error("password", "Invalid email or password. Please try again.")
            else:
                self._user = user
        return cleaned

    def get_user(self):
        return self._user   


class DonorRegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "First name",
                "id": "id_first_name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "Last name",
                "id": "id_last_name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "example@email.com",
                "id": "id_email",
            }
        ),
    )
    phone = forms.CharField(
        label="Phone",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "+20 10 1234 5678",
                "id": "id_phone",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "********",
                "id": "id_password1",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "********",
                "id": "id_password2",
            }
        ),
    )
    abo = forms.ChoiceField(
        label="Blood Type (ABO)",
        choices=BloodType.choices,
        widget=forms.Select(
            attrs={"class": "form-select custom-input", "id": "id_abo"}
        ),
    )
    rh = forms.ChoiceField(
        label="Rh Factor",
        choices=RhType.choices,
        widget=forms.Select(
            attrs={"class": "form-select custom-input", "id": "id_rh"}
        ),
    )
    city = forms.ModelChoiceField(
        label="City",
        queryset=City.objects.all(),
        widget=forms.Select(
            attrs={"class": "form-select custom-input", "id": "id_city"}
        ),
    )
    profile_picture = forms.ImageField(
        required=False,
        label="Profile Picture",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control custom-input", "id": "id_profile_picture"}
        ),
    )
    eligibility_consent = forms.BooleanField(
        required=False,
        label="I confirm that I meet the donation eligibility criteria.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input me-2"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            from .validators import validate_profile_image
            validate_profile_image(profile_picture)
        return profile_picture
    
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        if p1 != p2:
            raise ValidationError({"password2": "Passwords do not match."})
        validate_password_strength(p1)
        return cleaned

    # ✅ FIX: add save() method
    def save(self):
        cd = self.cleaned_data

        # Create user
        user = User.objects.create_user(
            first_name=cd["first_name"],
            last_name=cd["last_name"],
            email=cd["email"],
            password=cd["password1"],
            phone=cd.get("phone") or "",
            role="donor",
        )

        # Create donor profile
        donor = Donor.objects.create_donor(
            user_id=user.id,
            abo=cd["abo"],
            rh=cd["rh"],
            city_id=cd["city"].id,
            eligibility_consent=cd.get("eligibility_consent", False),
        )

        # Add profile picture if uploaded
        pic = cd.get("profile_picture")
        if pic:
            donor.profile_picture = pic
            donor.full_clean()
            donor.save(update_fields=["profile_picture"])

        return user, donor



class StaffRegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "First name",
                "id": "id_first_name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "Last name",
                "id": "id_last_name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "example@email.com",
                "id": "id_email",
            }
        ),
    )
    phone = forms.CharField(
        label="Phone",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "+20 10 1234 5678",
                "id": "id_phone",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "********",
                "id": "id_password1",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control custom-input",
                "placeholder": "********",
                "id": "id_password2",
            }
        ),
    )

    city = forms.ModelChoiceField(
        label="City",
        queryset=City.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select custom-input",
                "id": "id_city",
            }
        ),
        required=True,
    )
    hospital = forms.ModelChoiceField(
        label="Hospital",
        queryset=Hospital.objects.none(),
        widget=forms.Select(
            attrs={
                "class": "form-select custom-input",
                "id": "id_hospital",
            }
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Auto-filter hospitals based on selected city
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

class BloodRequestForm(forms.Form):
    abo = forms.ChoiceField(
        label="Blood Type (ABO)",
        choices=BloodType.choices,
        widget=forms.Select(attrs={"class": "form-select custom-input"}),
    )
    rh = forms.ChoiceField(
        label="Rh Factor",
        choices=RhType.choices,
        widget=forms.Select(attrs={"class": "form-select custom-input"}),
    )
    units_requested = forms.IntegerField(
        min_value=1,
        label="Number of Units",
        widget=forms.NumberInput(attrs={"class": "form-control custom-input", "placeholder": "Enter number of blood units"}),
    )
    deadline_at = forms.DateTimeField(
        label="Deadline",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control custom-input"}
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control custom-input", "rows": 3, "placeholder": "Optional notes or urgency details"}),
        required=False,
        label="Notes (optional)",
    )

    def __init__(self, *args, staff: Staff | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if staff is None:
            raise ValueError("BloodRequestForm requires a 'staff' instance.")
        self.staff = staff

    def clean_deadline_at(self):
        dt = self.cleaned_data["deadline_at"]
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        if dt <= timezone.now():
            raise ValidationError("Deadline must be in the future.")
        return dt

    def save(self):
        cd = self.cleaned_data
        hospital = self.staff.hospital
        city = hospital.city

        request = BloodRequest.objects.create(
            hospital=hospital,
            created_by=self.staff,
            units_requested=cd["units_requested"],
            abo=cd["abo"],
            rh=cd["rh"],
            city=city,
            deadline_at=cd["deadline_at"],
            notes=cd.get("notes", ""),
            status="open",
        )
        return request


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your name"
        })
    )

    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email"
        })
    )

    message = forms.CharField(
        label="Your Message",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Write your message..."
        })
    )
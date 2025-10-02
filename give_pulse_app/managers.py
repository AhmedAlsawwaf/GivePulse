import re
from typing import Optional

import bcrypt
from django.core.exceptions import ValidationError
from django.db import models
from .models import *

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s'\-]{1,149}$")  
EMAIL_RE = re.compile(r"^(?=.{6,254}$)[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,128}$")
BCRYPT_PREFIX_RE = re.compile(r"^\$2[aby]\$")

def _validate_name(label: str, value: str) -> None:
    if not value or not NAME_RE.fullmatch(value.strip()):
        raise ValidationError({label: f"Invalid {label.replace('_', ' ')}."})

def _validate_email(email: str) -> None:
    if not email or not EMAIL_RE.fullmatch(email.strip()):
        raise ValidationError({"email": "Invalid email address."})

def _validate_phone(phone: Optional[str]) -> None:
    if phone and not PHONE_RE.fullmatch(phone.strip()):
        raise ValidationError({"phone": "Invalid phone number."})

def _validate_password(password: str) -> None:
    if not password or not PASSWORD_RE.fullmatch(password):
        raise ValidationError({"password": "Min 8 chars, include upper/lower/digit/special."})

def _hash_password_if_needed(raw_or_hash: str) -> str:
    if BCRYPT_PREFIX_RE.match(raw_or_hash or ""):
        return raw_or_hash
    return bcrypt.hashpw(raw_or_hash.encode(), bcrypt.gensalt()).decode()

def check_password(raw_password: str, hashed: str) -> bool:
    if not BCRYPT_PREFIX_RE.match(hashed or ""):
        return False
    try:
        return bcrypt.checkpw(raw_password.encode(), hashed.encode())
    except Exception:
        return False


class UserManager(models.Manager):
    def create_user(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: str | None = None,
        role: str = "guest",
    ):
        _validate_name("first_name", first_name)
        _validate_name("last_name", last_name)
        _validate_email(email)
        _validate_phone(phone)
        _validate_password(password)

        user = User(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            phone=(phone or "").strip(),
            role=role,
            password=_hash_password_if_needed(password),
        )
        user.full_clean(exclude={"password"})
        user.save()
        return user

    def set_password(self, user_obj, new_password: str) -> None:
        _validate_password(new_password)
        user_obj.password = _hash_password_if_needed(new_password)
        user_obj.save(update_fields=["password", "updated_at"] if hasattr(user_obj, "updated_at") else ["password"])

    def authenticate(self, *, email: str, password: str):
        email_norm = (email or "").strip().lower()
        try:
            user = self.get(email=email_norm)
        except self.model.DoesNotExist:
            return None
        return user if check_password(password, user.password) else None


class StaffManager(models.Manager):
    def create_staff(self, *, user_id: int, hospital_id: int, role: str = "staff", is_verified: bool = False):
        staff = Staff(user_id=user_id, hospital_id=hospital_id, role=role, is_verified=is_verified)
        staff.full_clean()
        staff.save()
        return staff


class DonorManager(models.Manager):
    def create_donor(
        self,
        *,
        user_id: int,
        abo: str,
        rh: str,
        city_id: int,
        public_alias: str = "",
        eligibility_consent: bool = False,
        last_donation=None,
    ):
        city = City.objects.get(id=city_id)
        donor = Donor(
            user_id=user_id,
            abo=abo,
            rh=rh,
            city=city,
            public_alias=(public_alias or "").strip(),
            eligibility_consent=eligibility_consent,
            last_donation=last_donation,
        )
        donor.full_clean()
        donor.save()
        return donor

class BloodRequestManager(models.Manager):
    def create_request(
        self,
        *,
        hospital_id: int,
        created_by_id: int,
        units_requested: int,
        abo: str,
        rh: str,
        city_id: int,
        deadline_at,
        notes: str = "",
        status: str = "open",
    ):

        try:
            hospital = Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            raise ValidationError({"hospital": "Hospital not found."})

        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            raise ValidationError({"city": "City not found."})

        if hospital.city_id != city.id:
            raise ValidationError({"city": "City must match the hospital's city."})

        obj = BloodRequest(
            hospital=hospital,
            created_by_id=created_by_id,
            units_requested=units_requested,
            abo=abo,
            rh=rh,
            city=city,
            deadline_at=deadline_at,
            status=status,
            notes=(notes or "").strip(),
        )
        obj.full_clean()
        obj.save()
        return obj
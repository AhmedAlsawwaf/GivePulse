import re
from .validators import validate_password_strength
import bcrypt
from django.core.exceptions import ValidationError
from django.db import models

BCRYPT_PREFIX_RE = re.compile(r"^\$2[aby]\$")

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
    def create_user(self, *, first_name, last_name, email, password, phone=None, role="guest"):
        from .models import User
        validate_password_strength(password)
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

    def set_password(self, user_obj, new_password: str):
        validate_password_strength(new_password)
        user_obj.password = _hash_password_if_needed(new_password)
        fields = ["password"]
        if hasattr(user_obj, "updated_at"):
            fields.append("updated_at")
        user_obj.save(update_fields=fields)

    def authenticate(self, *, email: str, password: str):
        email_norm = (email or "").strip().lower()
        try:
            user = self.get(email=email_norm)
        except self.model.DoesNotExist:
            return None
        return user if check_password(password, user.password) else None


class StaffManager(models.Manager):
    def create_staff(self, *, user_id: int, hospital_id: int, role: str = "staff", is_verified: bool = False):
        from .models import Staff
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
        from .models import City,Donor
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
        from .models import City,Hospital,BloodRequest
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
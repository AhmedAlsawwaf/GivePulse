# give_pulse_app/validators.py
from __future__ import annotations
import re
from PIL import Image
from django.core.exceptions import ValidationError

NAME_RE  = re.compile(r"^[A-Za-z][A-Za-z\s'\-]{1,149}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,128}$")

def validate_person_name(value: str):
    if not value or not NAME_RE.fullmatch(value.strip()):
        raise ValidationError("Invalid name.")

def validate_phone(value: str):
    if value and not PHONE_RE.fullmatch(value.strip()):
        raise ValidationError("Invalid phone number.")

def validate_password_strength(raw_password: str):

    if not raw_password or not PASSWORD_RE.fullmatch(raw_password):
        raise ValidationError("Password must be 8–128 chars with upper, lower, digit, and special.")

def validate_profile_image(file, *, max_mb=2, min_px=128, max_px=3000):
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Image too large (>{max_mb}MB).")

    ct = getattr(file, "content_type", None)
    if ct and ct not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValidationError("Only JPEG, PNG, or WEBP images are allowed.")

    try:
        pos = file.tell()
        img = Image.open(file)
        img.verify()
        file.seek(pos)
        img = Image.open(file)
        w, h = img.size
        if w < min_px or h < min_px:
            raise ValidationError(f"Image is too small (min {min_px}x{min_px}).")
        if w > max_px or h > max_px:
            raise ValidationError(f"Image is too large (max {max_px}x{max_px}).")
    except Exception:
        raise ValidationError("Invalid image file.")
    finally:
        try:
            file.seek(0)
        except Exception:
            pass

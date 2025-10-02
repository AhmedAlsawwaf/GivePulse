from __future__ import annotations
import os, uuid

def donor_avatar_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"donors/{instance.user_id}/profile_{uuid.uuid4().hex}{ext}"

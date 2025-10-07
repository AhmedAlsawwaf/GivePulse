def user_context(request):
    """Add user context to all templates"""
    user = None
    if request.session.get("user_id"):
        try:
            from .models import User
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            # Clear invalid session
            for key in ("user_id", "user_role"):
                request.session.pop(key, None)
    
    return {"user": user}

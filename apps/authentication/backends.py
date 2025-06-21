from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        try:
            # Try multiple email field names that might exist in CustomUser
            user = User.objects.filter(
                Q(email=username) | 
                Q(email_address=username) | 
                Q(username=username)
            ).first()
            
            if user and user.check_password(password) and user.is_active:
                return user
                
        except Exception as e:
            # Log the error for debugging
            print(f"Authentication error: {e}")
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            

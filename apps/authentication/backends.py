from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    E-posta veya telefon ile giriş yapma backend'i
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # E-posta veya telefon ile kullanıcı ara
            user = User.objects.get(
                Q(email=username) | Q(phone=username) | Q(username=username)
            )
            
            # Şifre kontrolü
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            

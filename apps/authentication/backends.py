from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q # Q import'unu ekleyin

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    E-posta veya telefon ile giriş yapma backend'i
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        user = None
        try:
            # Kullanıcıyı e-posta veya telefon numarası ile bulmaya çalışın.
            # Q objeleri, OR koşullarıyla sorgu yapmayı sağlar.
            # .first() metodu, eşleşme olmazsa None, eşleşirse ilk objeyi döndürür,
            # böylece MultipleObjectsReturned hatasını önler.
            user = User.objects.filter(Q(email=username) | Q(phone=username)).first()
            
            # Eğer e-posta veya telefon ile bulunamazsa, USERNAME_FIELD olarak belirlenen
            # alan (models.py'de 'email' olarak belirlenmiş) üzerinden kullanıcı adı ile de denenebilir.
            # Ancak CustomUser modelinizde USERNAME_FIELD 'email' olduğu için
            # bu satır muhtemelen gereksizdir ve üstteki sorgu yeterli olacaktır.
            # Yine de AbstractUser'ın varsayılan username alanından kaynaklanabilecek durumlar için bırakılabilir.
            if not user:
                 user = User.objects.filter(username=username).first()

        except Exception as e:
            # Beklenmedik veritabanı sorgu hatalarını loglayın
            print(f"Error during user lookup in EmailBackend: {e}")
            return None


        # Kullanıcı bulunduysa şifreyi kontrol et ve aktif mi diye bak
        if user and user.check_password(password) and user.is_active:
            return user
        
        return None # Kullanıcı bulunamadı, şifre yanlış veya aktif değil
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
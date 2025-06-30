from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    """
    Kullanıcının rolünün izin verilen roller arasında olup olmadığını kontrol eden bir decorator.
    Kullanıcı giriş yapmamışsa login sayfasına, rolü yetersizse 403 hatası sayfasına yönlendirir.

    Kullanım:
    @login_required
    @role_required(allowed_roles=['admin'])
    def my_admin_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Önce kullanıcının giriş yapmış olduğundan emin olmalıyız.
            # Bu decorator'dan önce @login_required kullanılması tavsiye edilir.
            if not request.user.is_authenticated:
                return redirect('login')  # veya sizin login URL'nizin adı

            # Kullanıcının profilini ve rolünü al
            try:
                user_role = request.user.profile.role
            except AttributeError:
                # Eğer kullanıcının profili bir şekilde oluşmamışsa
                # veya 'profile' ilişkisi yoksa, erişimi reddet.
                raise PermissionDenied

            if user_role in allowed_roles:
                # Rolü uygunsa, asıl view fonksiyonunu çalıştır.
                return view_func(request, *args, **kwargs)
            else:
                # Rolü uygun değilse, PermissionDenied hatası fırlat.
                # Django bu hatayı varsayılan olarak 403 Forbidden sayfasına yönlendirir.
                raise PermissionDenied
        return _wrapped_view
    return decorator

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .decorators import role_required

# 1. Herkesin erişebileceği sayfa
def public_page(request):
    return HttpResponse("Burası herkese açık bir sayfadır.")

# 2. Sadece giriş yapmış kullanıcıların (User ve Admin) erişebileceği sayfa
@login_required
def user_dashboard(request):
    # request.user.profile.role sayesinde kullanıcının rolünü alabiliyoruz.
    user_role = request.user.profile.role
    return HttpResponse(f"Kullanıcı Paneline Hoş Geldiniz! Rolünüz: {user_role}")

# 3. Sadece 'admin' rolündeki kullanıcıların erişebileceği sayfa
@login_required
@role_required(allowed_roles=['admin'])
def admin_only_page(request):
    return HttpResponse("Burası sadece Admin'lerin görebileceği özel bir sayfadır.")

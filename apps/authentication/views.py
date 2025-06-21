from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # Debug: Print values
        print(f"Login attempt - Username: {username}, Password exists: {bool(password)}")
        
        user = authenticate(
            request=self.request,
            username=username,
            password=password
        )
        
        print(f"Authentication result: {user}")
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Giriş başarılı!')
            return redirect('/')
        else:
            messages.error(self.request, 'Email veya şifre hatalı!')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Giriş bilgilerinizi kontrol edin.')
        return super().form_invalid(form)
        

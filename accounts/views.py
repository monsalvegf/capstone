from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views

def home_view(request):
    if request.user.is_authenticated:
        # Importación dentro de la función para evitar importaciones cíclicas
        from nonconformities.models import Nonconformity
        return redirect('nonconformities:nonconformity_list')
    else:
        return auth_views.LoginView.as_view(template_name='accounts/login.html')(request)

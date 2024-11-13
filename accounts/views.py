from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

def home_view(request):
    if request.user.is_authenticated:
        return redirect('nonconformities:nonconformity_list')
    else:
        return auth_views.LoginView.as_view(template_name='registration/login.html')(request)

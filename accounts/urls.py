from django.urls import path
from django.contrib.auth import views as auth_views

# Definir el namespace para la aplicación 'accounts'
app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Puedes agregar otras rutas aquí...
]

from django.urls import path
from . import views

app_name = 'nonconformities'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Otras rutas...
]
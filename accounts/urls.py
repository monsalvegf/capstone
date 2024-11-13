from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home_view, name='home'),
    # Otras rutas de tu aplicación 'accounts'
]

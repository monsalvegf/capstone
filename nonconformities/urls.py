from django.urls import path
from . import views

app_name = 'nonconformities'

urlpatterns = [
    path('', views.nonconformity_list, name='nonconformity_list'),
    # Otras rutas...
]
from django.urls import path
from . import views

app_name = 'nonconformities'

urlpatterns = [
    path('', views.nonconformity_list, name='nonconformity_list'),
    path('export/', views.export_nonconformities, name='export'),
    path('detail/<int:pk>/', views.nonconformity_detail, name='nonconformity_detail'),
    path('detail/partial/<int:pk>/', views.nonconformity_detail_partial, name='nonconformity_detail_partial'),
    # ... otras rutas ...
]

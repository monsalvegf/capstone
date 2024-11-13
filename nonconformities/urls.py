from django.urls import path
from . import views

app_name = 'nonconformities'

urlpatterns = [
    path('', views.nonconformity_list, name='nonconformity_list'),
    path('detail/', views.nonconformity_detail_ajax, name='nonconformity_detail_ajax'),
    path('<int:pk>/', views.nonconformity_detail, name='nonconformity_detail'),
    # Agrega la ruta para la exportación si la tienes
    path('export/', views.export_nonconformities, name='export'),
]

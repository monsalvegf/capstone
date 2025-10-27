from django.urls import path
from . import views

app_name = 'nonconformities'

urlpatterns = [
    path('', views.nonconformity_list, name='nonconformity_list'),
    path('export/', views.export_nonconformities, name='export'),

    # CRUD de No Conformidades
    path('create/', views.create_nonconformity, name='create_nonconformity'),
    path('<int:pk>/edit/', views.update_nonconformity, name='update_nonconformity'),
    path('detail/<int:pk>/', views.nonconformity_detail, name='nonconformity_detail'),
    path('detail/partial/<int:pk>/', views.nonconformity_detail_partial, name='nonconformity_detail_partial'),

    # Gestión de estado
    path('<int:pk>/change-status/', views.change_status, name='change_status'),
    path('<int:pk>/close/', views.close_nonconformity, name='close_nonconformity'),
    path('<int:pk>/reopen/', views.reopen_nonconformity, name='reopen_nonconformity'),

    # Gestión de acciones
    path('<int:pk>/add-action/', views.add_action, name='add_action'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_form, name='main_form'),
    path('final_params/', views.final_params, name='final_params'),
    path('generate_config/', views.generate_config, name='generate_config'),
]

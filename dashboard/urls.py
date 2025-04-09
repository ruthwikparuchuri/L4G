from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    #path('', views.home, name='home'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('genai2025registration/', views.genai2025registration, name='genai2025registration'),
    path('l4g/', views.l4g, name='l4g'),
    path('college/', views.college, name='college'),
    path('genai2025/', views.genai2025, name='genai2025'),
    path('filter-genai2025-data/', views.filter_genai2025_data, name='filter_genai2025_data')

]

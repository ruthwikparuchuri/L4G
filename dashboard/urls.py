from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard:login'), name='logout'),
    path('login-success/', views.login_success, name='login_success'),

    path('genaisummerinternship/', views.genai_summer_internship_dashboard, name='genai_summer_internship_dashboard'),


    #path('', views.home, name='home'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('genai2025registration/', views.genai2025registration, name='genai2025registration'),
    path('l4g/', views.l4g, name='l4g'),
    path('college/', views.college, name='college'),
    path('genai2025/', views.genai2025, name='genai2025'),
    path('filter-genai2025-data/', views.filter_genai2025_data, name='filter_genai2025_data'),
    path('events/', views.eventlist, name='eventlist'),


    path('analytics/', views.college_dashboard_redirect, name='college_dashboard_redirect'),
    path('select/', views.college_redirect_by_l4gcode, name='college_redirect_by_l4gcode'),

    path('analytics/<str:l4g_code>/', views.college_dashboard_view, name='college_dashboard'),
    path('analytics/<str:l4g_code>/program/genai_internship_dashboard_2025/', views.genai_internship_dashboard_2025, name='genai_internship_dashboard_2025'),
    path('analytics/<str:l4g_code>/program/geminiworkshop_2025/', views.geminiworkshop_2025, name='geminiworkshop_2025'),
    path('analytics/<str:l4g_code>/program/genai_dashboard_2025/', views.genai_dashboard_2025, name='genai_dashboard_2025'),
    path('analytics/<str:l4g_code>/program/genai_dashboard_2024/', views.genai_dashboard_2024, name='genai_dashboard_2024'),
]
from django.urls import path
from django.shortcuts import render, redirect


from . import views

app_name = 'registration'  


urlpatterns = [
   path('genai2025/', views.learner_registration, name='learner_registration'),
   path('genai2025/registration-success/<str:status>/', views.registration_success, name='registration_success'),
   path('validate-rollno/', views.validate_rollno, name='validate_rollno'),
   path('validate-email/', views.validate_email, name='validate_email'),
   path('validate-url/', views.validate_url, name='validate_url'),
   path('autocomplete-college/', views.autocomplete_college,name='autocomplete_college'),
   path('validate-college/', views.validate_college, name='validate_college'),
   path('', views.test, name='test'),
   path("institution/", views.add_institution, name="add_institution"),
   path("load-states/", views.load_states, name="load_states"),
   path("load-districts/", views.load_districts, name="load_districts"),
   path('temporary-learners/', views.temporary_learners, name='temporary_learners'),
   path('get-approved-students/', views.get_approved_students, name='get_approved_students'),
   path('approve-learner/', views.approve_learner, name='approve_learner'),
   path('update-approval/<int:request_id>/', views.update_approval_status, name='update_approval_status'),
   path('geminiworkshop2025/', views.gemini_workshop_registration, name='gemini_workshop_2025'),
   path("check_rollnumber/", views.check_rollnumber, name="check_rollnumber"),
   path('validate_ai_email/', views.validate_ai_email, name='validate_ai_email'),
   path('check_pr2/', views.check_pr2, name='check_pr2'),
   path('fetch-events/', views.fetch_events, name='fetch_events'),
   path('add-event/', views.add_event, name='add_event'),
   path("search-trainers/", views.search_trainers, name="search_trainers"),
   path('add-trainer/', views.add_trainer, name='add_trainer'),
   path('autocomplete-learner/', views.autocomplete_learner, name='autocomplete_learner'),
   path("feedback/", views.workshop_feedback, name="workshop_feedback"),
   path('manage-events/', views.event_status_manage, name='manage_events'),
   path("validate_developer_url/", views.validate_developer_url, name="validate_developer_url"),

]




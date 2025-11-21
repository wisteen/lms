from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('school-fees/', views.school_fees, name='school_fees'),
    path('academics/', views.academics, name='academics'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('admissions/inquiry/', views.admissions_inquiry, name='admissions_inquiry'),
]

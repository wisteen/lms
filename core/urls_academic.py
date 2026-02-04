"""
URL patterns for Academic Management System
"""

from django.urls import path
from . import views_academic

app_name = 'academic'

urlpatterns = [
    # Curriculum Management URLs
    path('curriculum/', views_academic.curriculum_list, name='curriculum_list'),
    path('curriculum/create/', views_academic.curriculum_create, name='curriculum_create'),
    path('curriculum/<int:curriculum_id>/', views_academic.curriculum_detail, name='curriculum_detail'),
    path('curriculum/<int:curriculum_id>/edit/', views_academic.curriculum_edit, name='curriculum_edit'),
    
    # Lesson Planning URLs
    path('lesson-plans/', views_academic.lesson_plan_list, name='lesson_plan_list'),
    path('lesson-plans/create/', views_academic.lesson_plan_create, name='lesson_plan_create'),
    path('lesson-plans/<int:lesson_plan_id>/', views_academic.lesson_plan_detail, name='lesson_plan_detail'),
    path('lesson-plans/<int:lesson_plan_id>/edit/', views_academic.lesson_plan_edit, name='lesson_plan_edit'),
    path('lesson-plans/<int:lesson_plan_id>/toggle-completion/', views_academic.toggle_lesson_completion, name='toggle_lesson_completion'),
    
    # Coverage Tracking URLs
    path('coverage-report/', views_academic.coverage_report, name='coverage_report'),
    
    # Assignment Management URLs
    path('assignments/', views_academic.assignment_list, name='assignment_list'),
    path('assignments/create/', views_academic.assignment_create, name='assignment_create'),
    path('assignments/<int:assignment_id>/', views_academic.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/edit/', views_academic.assignment_edit, name='assignment_edit'),
    path('assignments/<int:assignment_id>/submit/', views_academic.submit_assignment, name='submit_assignment'),
    path('submissions/<int:submission_id>/grade/', views_academic.grade_submission, name='grade_submission'),
    
    # Academic Calendar URLs
    path('calendar/', views_academic.academic_calendar, name='calendar'),
    
    # AJAX URLs
    path('api/learning-objectives/', views_academic.get_learning_objectives, name='get_learning_objectives'),
    
    # Student URLs
    path('student/curriculum/', views_academic.student_curriculum_view, name='student_curriculum'),
    path('student/lesson-plans/', views_academic.student_lesson_plans_view, name='student_lesson_plans'),
]
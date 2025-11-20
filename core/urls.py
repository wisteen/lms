from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('student/results/', views.student_results, name='student_results'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    
    # Teacher URLs
    path('teacher/results/', views.manage_results, name='manage_results'),
    path('teacher/results-overview/', views.results_overview, name='results_overview'),
    path('teacher/analytics/', views.view_analytics, name='view_analytics'),
    path('teacher/export-results/', views.export_results, name='export_results'),
    path('teacher/component-results/', views.component_results, name='component_results'),
    path('teacher/quiz/', views.quiz_management, name='quiz_management'),
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    path('teacher/quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('teacher/quiz/<int:quiz_id>/questions/', views.add_questions, name='add_questions'),
    path('teacher/question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('api/delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('teacher/question-bank/', views.question_bank, name='question_bank'),
    path('api/add-question-from-bank/', views.add_question_from_bank, name='add_question_from_bank'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('teacher/quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('teacher/quiz/<int:quiz_id>/grade-theory/', views.grade_theory, name='grade_theory'),
    path('api/delete-quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('api/students-by-class/', views.get_students_by_class, name='get_students_by_class'),
    path('api/recent-results/', views.get_recent_results, name='get_recent_results'),
    path('api/get-components/', views.get_components, name='get_components'),
    path('api/get-student-results/', views.get_student_results, name='get_student_results'),
    path('api/update-component-score/', views.update_component_score, name='update_component_score'),
    
    # Class Teacher URLs
    path('class-teacher/broadsheet/', views.class_broadsheet, name='class_broadsheet'),
    path('class-teacher/attendance/', views.manage_attendance, name='manage_attendance'),
    path('class-teacher/promotion/', views.student_promotion, name='student_promotion'),
    path('api/promote-students/', views.promote_students, name='promote_students'),
    path('api/revert-promotion/', views.revert_promotion, name='revert_promotion'),
    
    # Enhanced Quiz
    path('enhanced-quiz/<int:quiz_id>/', views.enhanced_quiz, name='enhanced_quiz'),
    path('view-quiz-result/<int:quiz_id>/', views.view_quiz_result, name='view_quiz_result'),
    
    # Result Checking
    path('check-result/', views.check_result, name='check_result'),
    path('result-card/<str:token>/', views.view_result_card, name='view_result_card'),
    path('generate-tokens/', views.generate_tokens, name='generate_tokens'),
]
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'stream', 'created_at')
    search_fields = ('name', 'stream')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'pass_mark', 'created_at')
    search_fields = ('name', 'code')

@admin.register(GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    list_display = ('grade', 'min_score', 'max_score', 'grade_point', 'remark')
    ordering = ['-min_score']

@admin.register(ResultComponent)
class ResultComponentAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'component_name', 'weight', 'max_score')
    list_filter = ('school_class', 'subject')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'school_class', 'is_promoted', 'promoted_to')
    list_filter = ('school_class', 'is_promoted')
    search_fields = ('student_id', 'user__first_name', 'user__last_name')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')
    filter_horizontal = ('subjects', 'classes')

@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school_class')
    list_filter = ('school_class',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)

@admin.register(ComponentResult)
class ComponentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'component', 'term', 'score')
    list_filter = ('term', 'component__subject')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'total_score', 'grade', 'grade_point')
    list_filter = ('term', 'subject', 'grade')
    search_fields = ('student__student_id', 'student__user__first_name')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'school_class', 'teacher', 'status', 'start_time')
    list_filter = ('status', 'subject', 'school_class', 'shuffle_questions', 'full_screen_mode')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_type', 'question_text', 'max_marks')
    list_filter = ('question_type', 'quiz__subject')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'final_score', 'is_submitted', 'is_graded', 'tab_switches')
    list_filter = ('is_submitted', 'is_graded', 'quiz__subject')

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct', 'manual_score')
    list_filter = ('is_correct', 'question__question_type')


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'principal_name', 'proprietor_name')


@admin.register(Psychomotor)
class PsychomotorAdmin(admin.ModelAdmin):
    list_display = ('student', 'term')
    list_filter = ('term', 'student__school_class')


@admin.register(EffectiveDomain)
class EffectiveDomainAdmin(admin.ModelAdmin):
    list_display = ('student', 'term')
    list_filter = ('term', 'student__school_class')

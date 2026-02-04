"""
Views for Academic Management System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from datetime import timedelta
import json

from .models import (
    Curriculum, LearningObjective, SyllabusContent, LessonPlan, CurriculumCoverage,
    AcademicEvent, Holiday, ExamSchedule, TimeSlot, Timetable, RoomAssignment,
    Assignment, AssignmentSubmission, SubmissionFile,
    Subject, SchoolClass, Teacher, Student, Term
)
from .forms_academic import (
    CurriculumForm, LearningObjectiveForm, SyllabusContentForm, LessonPlanForm,
    AcademicEventForm, HolidayForm, TimeSlotForm, TimetableForm,
    AssignmentForm, AssignmentSubmissionForm, SubmissionFileForm,
    LearningObjectiveFormSet, SyllabusContentFormSet
)
from .services_academic import (
    CoverageTracker, CalendarManager, TimetableBuilder, 
    AssignmentTracker, ReportGenerator
)


# Curriculum Management Views

@login_required
def curriculum_list(request):
    """List all curricula with filtering options"""
    
    curricula = Curriculum.objects.all().select_related('created_by').prefetch_related('subjects')
    
    # Filter by user role
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher:
            curricula = curricula.filter(subjects__in=teacher.subjects.all()).distinct()
    
    # Search and filter
    search = request.GET.get('search')
    if search:
        curricula = curricula.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    academic_year = request.GET.get('academic_year')
    if academic_year:
        curricula = curricula.filter(academic_year=academic_year)
    
    subject_id = request.GET.get('subject')
    if subject_id:
        curricula = curricula.filter(subjects__id=subject_id)
    
    # Pagination
    paginator = Paginator(curricula, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'subjects': Subject.objects.all(),
        'academic_years': Curriculum.objects.values_list('academic_year', flat=True).distinct(),
        'search': search,
        'selected_academic_year': academic_year,
        'selected_subject': subject_id,
    }
    
    return render(request, 'academic/curriculum_list.html', context)


@login_required
def curriculum_detail(request, curriculum_id):
    """View curriculum details with learning objectives and syllabus"""
    
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    
    # Check permissions
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher and not curriculum.subjects.filter(id__in=teacher.subjects.all()).exists():
            messages.error(request, 'You do not have permission to view this curriculum.')
            return redirect('academic:curriculum_list')
    
    learning_objectives = curriculum.learning_objectives.all().order_by('subject', 'order')
    syllabus_contents = curriculum.syllabus_contents.all().order_by('subject', 'order')
    
    context = {
        'curriculum': curriculum,
        'learning_objectives': learning_objectives,
        'syllabus_contents': syllabus_contents,
    }
    
    return render(request, 'academic/curriculum_detail.html', context)


@login_required
def curriculum_create(request):
    """Create a new curriculum"""
    
    if request.user.role not in ['super_admin', 'subject_teacher']:
        messages.error(request, 'You do not have permission to create curricula.')
        return redirect('academic:curriculum_list')
    
    if request.method == 'POST':
        form = CurriculumForm(request.POST, user=request.user)
        
        if form.is_valid():
            curriculum = form.save(commit=False)
            curriculum.created_by = request.user
            curriculum.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, 'Curriculum created successfully. You can now add learning objectives and syllabus content.')
            return redirect('academic:curriculum_edit', curriculum_id=curriculum.id)
    else:
        form = CurriculumForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'academic/curriculum_form.html', context)


@login_required
def curriculum_edit(request, curriculum_id):
    """Edit an existing curriculum"""
    
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    
    # Check permissions
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher and curriculum.created_by != request.user:
            messages.error(request, 'You can only edit curricula you created.')
            return redirect('academic:curriculum_detail', curriculum_id=curriculum.id)
    elif request.user.role not in ['super_admin']:
        messages.error(request, 'You do not have permission to edit this curriculum.')
        return redirect('academic:curriculum_detail', curriculum_id=curriculum.id)
    
    if request.method == 'POST':
        form = CurriculumForm(request.POST, instance=curriculum, user=request.user)
        objective_formset = LearningObjectiveFormSet(request.POST, instance=curriculum, prefix='objectives')
        syllabus_formset = SyllabusContentFormSet(request.POST, instance=curriculum, prefix='syllabus')
        
        if form.is_valid() and objective_formset.is_valid() and syllabus_formset.is_valid():
            curriculum = form.save()
            objective_formset.save()
            syllabus_formset.save()
            
            messages.success(request, 'Curriculum updated successfully.')
            return redirect('academic:curriculum_detail', curriculum_id=curriculum.id)
    else:
        form = CurriculumForm(instance=curriculum, user=request.user)
        objective_formset = LearningObjectiveFormSet(instance=curriculum, prefix='objectives')
        syllabus_formset = SyllabusContentFormSet(instance=curriculum, prefix='syllabus')
    
    context = {
        'form': form,
        'objective_formset': objective_formset,
        'syllabus_formset': syllabus_formset,
        'curriculum': curriculum,
        'action': 'Edit',
    }
    
    return render(request, 'academic/curriculum_form.html', context)


# Lesson Planning Views

@login_required
def lesson_plan_list(request):
    """List lesson plans for teachers"""
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can access lesson plans.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    lesson_plans = LessonPlan.objects.filter(teacher=teacher).select_related(
        'curriculum', 'subject', 'school_class'
    ).order_by('-created_at')
    
    # Filter options
    curriculum_id = request.GET.get('curriculum')
    if curriculum_id:
        lesson_plans = lesson_plans.filter(curriculum_id=curriculum_id)
    
    subject_id = request.GET.get('subject')
    if subject_id:
        lesson_plans = lesson_plans.filter(subject_id=subject_id)
    
    class_id = request.GET.get('class')
    if class_id:
        lesson_plans = lesson_plans.filter(school_class_id=class_id)
    
    is_completed = request.GET.get('completed')
    if is_completed == 'true':
        lesson_plans = lesson_plans.filter(is_completed=True)
    elif is_completed == 'false':
        lesson_plans = lesson_plans.filter(is_completed=False)
    
    # Pagination
    paginator = Paginator(lesson_plans, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'teacher': teacher,
        'curricula': Curriculum.objects.filter(subjects__in=teacher.subjects.all(), is_published=True).distinct(),
        'subjects': teacher.subjects.all(),
        'classes': teacher.classes.all(),
    }
    
    return render(request, 'academic/lesson_plan_list.html', context)


@login_required
def lesson_plan_create(request):
    """Create a new lesson plan"""
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can create lesson plans.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'POST':
        form = LessonPlanForm(request.POST, user=request.user)
        
        if form.is_valid():
            lesson_plan = form.save(commit=False)
            lesson_plan.teacher = teacher
            lesson_plan.save()
            form.save_m2m()  # Save learning objectives
            
            messages.success(request, 'Lesson plan created successfully.')
            return redirect('academic:lesson_plan_detail', lesson_plan_id=lesson_plan.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LessonPlanForm(user=request.user)
    
    context = {
        'form': form,
        'teacher': teacher,
        'action': 'Create',
    }
    
    return render(request, 'academic/lesson_plan_form.html', context)


@login_required
def lesson_plan_detail(request, lesson_plan_id):
    """View lesson plan details"""
    
    lesson_plan = get_object_or_404(LessonPlan, id=lesson_plan_id)
    
    # Check permissions
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher and lesson_plan.teacher != teacher:
            messages.error(request, 'You can only view your own lesson plans.')
            return redirect('academic:lesson_plan_list')
    
    context = {
        'lesson_plan': lesson_plan,
    }
    
    return render(request, 'academic/lesson_plan_detail.html', context)


@login_required
def lesson_plan_edit(request, lesson_plan_id):
    """Edit an existing lesson plan"""
    
    lesson_plan = get_object_or_404(LessonPlan, id=lesson_plan_id)
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can edit lesson plans.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if lesson_plan.teacher != teacher:
        messages.error(request, 'You can only edit your own lesson plans.')
        return redirect('academic:lesson_plan_detail', lesson_plan_id=lesson_plan.id)
    
    if request.method == 'POST':
        form = LessonPlanForm(request.POST, instance=lesson_plan, user=request.user)
        
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Lesson plan updated successfully.')
            return redirect('academic:lesson_plan_detail', lesson_plan_id=lesson_plan.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LessonPlanForm(instance=lesson_plan, user=request.user)
    
    context = {
        'form': form,
        'lesson_plan': lesson_plan,
        'teacher': teacher,
        'action': 'Edit',
    }
    
    return render(request, 'academic/lesson_plan_form.html', context)


@login_required
def toggle_lesson_completion(request, lesson_plan_id):
    """Toggle lesson plan completion status"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    lesson_plan = get_object_or_404(LessonPlan, id=lesson_plan_id)
    
    # Check permissions
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher and lesson_plan.teacher != teacher:
            return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    # Toggle completion
    lesson_plan.is_completed = not lesson_plan.is_completed
    lesson_plan.save()
    
    return JsonResponse({
        'success': True,
        'is_completed': lesson_plan.is_completed,
        'completion_date': lesson_plan.completion_date.isoformat() if lesson_plan.completion_date else None
    })


# Coverage Tracking Views

@login_required
def coverage_report(request):
    """View curriculum coverage reports"""
    
    if request.user.role not in ['subject_teacher', 'class_teacher', 'super_admin']:
        messages.error(request, 'You do not have permission to view coverage reports.')
        return redirect('dashboard')
    
    curriculum_id = request.GET.get('curriculum')
    class_id = request.GET.get('class')
    
    if curriculum_id and class_id:
        curriculum = get_object_or_404(Curriculum, id=curriculum_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        
        # Check permissions
        if request.user.role == 'subject_teacher':
            teacher = getattr(request.user, 'teacher', None)
            if teacher:
                if not curriculum.subjects.filter(id__in=teacher.subjects.all()).exists():
                    messages.error(request, 'You do not have permission to view this curriculum.')
                    return redirect('academic:coverage_report')
                if school_class not in teacher.classes.all():
                    messages.error(request, 'You do not have permission to view this class.')
                    return redirect('academic:coverage_report')
        
        report_data = ReportGenerator.generate_curriculum_coverage_report(curriculum, school_class)
        
        context = {
            'report_data': report_data['statistics'],
            'coverage_by_objective': report_data['coverage_data'],
            'objectives_by_subject': report_data['objectives_by_subject'],
            'curriculum': curriculum,
            'school_class': school_class,
            'completed_objectives': report_data['statistics']['completed_objectives'],
            'at_risk_objectives': report_data['statistics']['at_risk_objectives'],
            'total_objectives': report_data['statistics']['total_objectives'],
            'overall_coverage': report_data['statistics']['overall_completion_percentage'],
        }
        
        return render(request, 'academic/coverage_report_detail.html', context)
    
    # Show selection form
    curricula = Curriculum.objects.filter(is_published=True)
    classes = SchoolClass.objects.all()
    
    if request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher:
            curricula = curricula.filter(subjects__in=teacher.subjects.all()).distinct()
            classes = teacher.classes.all()
    
    context = {
        'curricula': curricula,
        'classes': classes,
    }
    
    return render(request, 'academic/coverage_report.html', context)


# Assignment Management Views

@login_required
def assignment_list(request):
    """List assignments based on user role"""
    
    if request.user.role == 'student':
        return student_assignment_list(request)
    elif request.user.role in ['subject_teacher', 'class_teacher']:
        return teacher_assignment_list(request)
    else:
        messages.error(request, 'You do not have permission to view assignments.')
        return redirect('dashboard')


def student_assignment_list(request):
    """List assignments for students"""
    
    student = get_object_or_404(Student, user=request.user)
    assignment_info = AssignmentTracker.get_student_assignments(student, include_completed=True)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'pending':
        assignment_info = [info for info in assignment_info if not info['is_submitted']]
    elif status == 'submitted':
        assignment_info = [info for info in assignment_info if info['is_submitted']]
    elif status == 'overdue':
        assignment_info = [info for info in assignment_info if info['is_overdue']]
    
    context = {
        'assignment_info': assignment_info,
        'student': student,
        'status_filter': status,
    }
    
    return render(request, 'academic/student_assignment_list.html', context)


def teacher_assignment_list(request):
    """List assignments for teachers"""
    
    teacher = get_object_or_404(Teacher, user=request.user)
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    
    # Add submission statistics
    assignment_data = []
    for assignment in assignments:
        stats = AssignmentTracker.get_submission_statistics(assignment)
        assignment_data.append({
            'assignment': assignment,
            'stats': stats
        })
    
    context = {
        'assignment_data': assignment_data,
        'teacher': teacher,
    }
    
    return render(request, 'academic/teacher_assignment_list.html', context)


@login_required
def assignment_create(request):
    """Create a new assignment"""
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can create assignments.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = teacher
            assignment.save()
            form.save_m2m()  # Save school classes
            
            messages.success(request, 'Assignment created successfully.')
            return redirect('academic:assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(user=request.user)
    
    context = {
        'form': form,
        'teacher': teacher,
        'action': 'Create',
    }
    
    return render(request, 'academic/assignment_form.html', context)


@login_required
def assignment_edit(request, assignment_id):
    """Edit an existing assignment"""
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can edit assignments.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if assignment.teacher != teacher:
        messages.error(request, 'You can only edit your own assignments.')
        return redirect('academic:assignment_detail', assignment_id=assignment.id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, user=request.user)
        
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Assignment updated successfully.')
            return redirect('academic:assignment_detail', assignment_id=assignment.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentForm(instance=assignment, user=request.user)
    
    context = {
        'form': form,
        'assignment': assignment,
        'teacher': teacher,
        'action': 'Edit',
    }
    
    return render(request, 'academic/assignment_form.html', context)


@login_required
def assignment_detail(request, assignment_id):
    """View assignment details"""
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check permissions and get appropriate context
    if request.user.role == 'student':
        student = get_object_or_404(Student, user=request.user)
        
        # Check if student is in assigned classes
        if student.school_class not in assignment.school_classes.all():
            messages.error(request, 'You are not assigned to this assignment.')
            return redirect('academic:assignment_list')
        
        # Get submission if exists
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=student)
        except AssignmentSubmission.DoesNotExist:
            submission = None
        
        context = {
            'assignment': assignment,
            'submission': submission,
            'student': student,
            'can_submit': not assignment.is_overdue() or assignment.allow_late_submission,
        }
        
        return render(request, 'academic/student_assignment_detail.html', context)
    
    elif request.user.role == 'subject_teacher':
        teacher = getattr(request.user, 'teacher', None)
        if teacher and assignment.teacher != teacher:
            messages.error(request, 'You can only view your own assignments.')
            return redirect('academic:assignment_list')
        
        stats = AssignmentTracker.get_submission_statistics(assignment)
        submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student__user')
        
        context = {
            'assignment': assignment,
            'stats': stats,
            'submissions': submissions,
            'teacher': teacher,
        }
        
        return render(request, 'academic/teacher_assignment_detail.html', context)
    
    else:
        messages.error(request, 'You do not have permission to view this assignment.')
        return redirect('dashboard')


@login_required
def submit_assignment(request, assignment_id):
    """Submit an assignment (for students)"""
    
    if request.user.role != 'student':
        messages.error(request, 'Only students can submit assignments.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = get_object_or_404(Student, user=request.user)
    
    # Check if student is in assigned classes
    if student.school_class not in assignment.school_classes.all():
        messages.error(request, 'You are not assigned to this assignment.')
        return redirect('academic:assignment_list')
    
    # Check if assignment is overdue and late submissions not allowed
    if assignment.is_overdue() and not assignment.allow_late_submission:
        messages.error(request, 'This assignment is overdue and late submissions are not allowed.')
        return redirect('academic:assignment_detail', assignment_id=assignment.id)
    
    # Check if already submitted and graded
    existing_submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=student
    ).first()
    
    if existing_submission and existing_submission.score is not None:
        messages.error(request, 'This assignment has been graded. You cannot edit your submission.')
        return redirect('academic:assignment_detail', assignment_id=assignment.id)
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, assignment=assignment, instance=existing_submission)
        
        if form.is_valid():
            has_text = form.cleaned_data.get('submission_text', '').strip()
            has_file = request.FILES.get('file')
            
            if not has_text and not has_file:
                messages.error(request, 'Please provide either a text response or upload a file.')
            else:
                submission = form.save(commit=False)
                if not existing_submission:
                    submission.assignment = assignment
                    submission.student = student
                submission.save()
                
                # Handle file uploads
                if has_file:
                    SubmissionFile.objects.create(
                        submission=submission,
                        file=has_file,
                        original_filename=has_file.name
                    )
                
                messages.success(request, 'Assignment submitted successfully.')
                return redirect('academic:assignment_detail', assignment_id=assignment.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentSubmissionForm(assignment=assignment, instance=existing_submission)
    
    context = {
        'assignment': assignment,
        'form': form,
        'existing_submission': existing_submission,
        'student': student,
    }
    
    return render(request, 'academic/submit_assignment.html', context)


# Academic Calendar Views

@login_required
def academic_calendar(request):
    """View academic calendar"""
    
    # Get current academic year or from request
    current_year = timezone.now().year
    academic_year = request.GET.get('year', f"{current_year}-{current_year + 1}")
    
    # Get events for the academic year
    events = AcademicEvent.objects.filter(academic_year=academic_year).order_by('start_date')
    holidays = Holiday.objects.filter(academic_year=academic_year).order_by('date')
    
    # Filter by user role
    if request.user.role == 'student':
        student = getattr(request.user, 'student', None)
        if student:
            # Show events relevant to student's class
            events = events.filter(
                Q(terms__in=Term.objects.filter(is_active=True)) |
                Q(event_type='holiday')
            )
    
    context = {
        'events': events,
        'holidays': holidays,
        'academic_year': academic_year,
        'available_years': AcademicEvent.objects.values_list('academic_year', flat=True).distinct(),
    }
    
    return render(request, 'academic/calendar.html', context)


# AJAX Views

@login_required
def get_learning_objectives(request):
    """Get learning objectives for a curriculum and subject (AJAX)"""
    
    curriculum_id = request.GET.get('curriculum_id')
    subject_id = request.GET.get('subject_id')
    
    if curriculum_id and subject_id:
        objectives = LearningObjective.objects.filter(
            curriculum_id=curriculum_id,
            subject_id=subject_id
        ).values('id', 'title', 'description')
        
        return JsonResponse({'objectives': list(objectives)})
    
    return JsonResponse({'objectives': []})


@login_required
def student_curriculum_view(request):
    """View curriculum for students"""
    
    if request.user.role != 'student':
        messages.error(request, 'Only students can access this page.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, user=request.user)
    
    # Get published curricula
    curricula = Curriculum.objects.filter(
        is_published=True
    ).distinct().prefetch_related('subjects', 'learning_objectives')
    
    context = {
        'curricula': curricula,
        'student': student,
    }
    
    return render(request, 'academic/student_curriculum_list.html', context)


@login_required
def student_lesson_plans_view(request):
    """View lesson plans for students"""
    
    if request.user.role != 'student':
        messages.error(request, 'Only students can access this page.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, user=request.user)
    
    # Get lesson plans for student's class
    lesson_plans = LessonPlan.objects.filter(
        school_class=student.school_class
    ).select_related('curriculum', 'subject', 'teacher').order_by('-created_at')
    
    context = {
        'lesson_plans': lesson_plans,
        'student': student,
    }
    
    return render(request, 'academic/student_lesson_plans.html', context)


@login_required
def grade_submission(request, submission_id):
    """Grade a student submission"""
    
    if request.user.role != 'subject_teacher':
        messages.error(request, 'Only teachers can grade submissions.')
        return redirect('dashboard')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if submission.assignment.teacher != teacher:
        messages.error(request, 'You can only grade submissions for your own assignments.')
        return redirect('academic:assignment_list')
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback', '')
        
        if score:
            submission.score = score
        submission.feedback = feedback
        submission.save()
        
        messages.success(request, 'Submission graded successfully.')
        return redirect('academic:assignment_detail', assignment_id=submission.assignment.id)
    
    context = {
        'submission': submission,
    }
    
    return render(request, 'academic/grade_submission.html', context)
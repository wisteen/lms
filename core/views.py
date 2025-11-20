from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from .models import *

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'auth/login.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.role == 'student':
        student = Student.objects.get(user=user)
        context.update({
            'student': student,
            'live_quizzes': Quiz.objects.filter(
                school_class=student.school_class,
                status='live'
            ),
            'recent_results': Result.objects.filter(student=student).order_by('-created_at')[:5]
        })
        return render(request, 'dashboards/student.html', context)
    
    elif user.role == 'subject_teacher':
        teacher = Teacher.objects.get(user=user)
        
        # Check if also a class teacher
        try:
            class_teacher = ClassTeacher.objects.get(teacher=teacher)
            context['class_teacher'] = class_teacher
        except ClassTeacher.DoesNotExist:
            pass

        context.update({
            'teacher': teacher,
            'my_classes': teacher.classes.all(),
            'my_subjects': teacher.subjects.all(),
            'pending_results': Result.objects.filter(
                subject__in=teacher.subjects.all(),
                student__school_class__in=teacher.classes.all(),
                total_score=0
            ).count()
        })
        return render(request, 'dashboards/subject_teacher.html', context)
    
    elif user.role == 'class_teacher':
        teacher = Teacher.objects.get(user=user)
        class_teacher = ClassTeacher.objects.get(teacher=teacher)
        students = Student.objects.filter(school_class=class_teacher.school_class)
        context.update({
            'teacher': teacher,
            'class_teacher': class_teacher,
            'students': students,
            'class_average': Result.objects.filter(
                student__school_class=class_teacher.school_class
            ).aggregate(avg=Avg('total_score'))['avg'] or 0
        })
        return render(request, 'dashboards/class_teacher.html', context)
    
    elif user.role == 'super_admin':
        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_classes': SchoolClass.objects.count(),
            'total_subjects': Subject.objects.count(),
        })
        return render(request, 'dashboards/super_admin.html', context)
    
    return render(request, 'dashboards/default.html', context)

@login_required
def get_students_by_class(request):
    """AJAX view to get students for a specific class"""
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(school_class_id=class_id).select_related('user')
        student_data = [
            {
                'id': student.id,
                'name': student.user.get_full_name(),
                'student_id': student.student_id
            }
            for student in students
        ]
        return JsonResponse({'students': student_data})
    return JsonResponse({'students': []})

@login_required
def get_recent_results(request):
    """AJAX view to get recent results for a class and subject"""
    if request.user.role != 'subject_teacher':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    
    if class_id and subject_id:
        teacher = Teacher.objects.get(user=request.user)
        
        # Verify teacher can access this data
        if not (teacher.classes.filter(id=class_id).exists() and 
                teacher.subjects.filter(id=subject_id).exists()):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        results = Result.objects.filter(
            student__school_class_id=class_id,
            subject_id=subject_id
        ).select_related('student__user', 'term').order_by('-updated_at')[:10]
        
        result_data = [
            {
                'student_name': result.student.user.get_full_name(),
                'student_id': result.student.student_id,
                'total_score': float(result.total_score),
                'grade': result.grade,
                'grade_point': float(result.grade_point),
                'remark': result.remark,
                'term': result.term.name,
                'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M')
            }
            for result in results
        ]
        return JsonResponse({'results': result_data})
    
    return JsonResponse({'results': []})

@login_required
def student_results(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    student = Student.objects.get(user=request.user)
    results = Result.objects.filter(student=student).order_by('-term__start_date', 'subject__name')
    return render(request, 'student/results.html', {'results': results})

@login_required
def take_quiz(request, quiz_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = Student.objects.get(user=request.user)
    
    if not quiz.is_live():
        messages.error(request, 'Quiz is not currently available')
        return redirect('dashboard')
    
    attempt, created = QuizAttempt.objects.get_or_create(
        quiz=quiz, student=student,
        defaults={'start_time': timezone.now()}
    )
    
    if attempt.is_submitted:
        messages.info(request, 'You have already submitted this quiz')
        return redirect('dashboard')
    
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                QuizAnswer.objects.update_or_create(
                    attempt=attempt, question=question,
                    defaults={'selected_answer': answer}
                )
        
        attempt.end_time = timezone.now()
        attempt.is_submitted = True
        
        # Calculate score
        correct_answers = attempt.answers.filter(is_correct=True).count()
        total_questions = questions.count()
        attempt.score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        attempt.save()
        
        messages.success(request, f'Quiz submitted! Your score: {attempt.score:.1f}%')
        return redirect('dashboard')
    
    return render(request, 'student/quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'attempt': attempt
    })

@login_required
def manage_results(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    
    if request.method == 'POST':
        messages.info(request, 'Please use the Component Results system for entering scores.')
        return redirect('component_results')
    
    classes = teacher.classes.all()
    subjects = teacher.subjects.all()
    active_term = Term.objects.filter(is_active=True).first()
    
    return render(request, 'teacher/manage_results.html', {
        'classes': classes,
        'subjects': subjects,
        'active_term': active_term
    })

@login_required
def create_quiz(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    
    if request.method == 'POST':
        quiz = Quiz.objects.create(
            title=request.POST.get('title'),
            subject_id=request.POST.get('subject'),
            school_class_id=request.POST.get('class'),
            teacher=teacher,
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            duration_minutes=int(request.POST.get('duration_minutes', 60)),
            instructions=request.POST.get('instructions', ''),
            shuffle_questions=request.POST.get('shuffle_questions') == 'on',
            shuffle_options=request.POST.get('shuffle_options') == 'on',
            full_screen_mode=request.POST.get('full_screen_mode') == 'on',
            detect_tab_switching=request.POST.get('detect_tab_switching') == 'on',
            max_tab_switches=int(request.POST.get('max_tab_switches', 3)),
            status='draft'
        )
        
        messages.success(request, 'Quiz created successfully')
        return redirect('add_questions', quiz_id=quiz.id)
    
    return render(request, 'teacher/create_quiz.html', {
        'subjects': teacher.subjects.all(),
        'classes': teacher.classes.all()
    })

@login_required
def quiz_management(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    quizzes = Quiz.objects.filter(teacher=teacher).order_by('-created_at')
    
    return render(request, 'teacher/quiz_management.html', {'quizzes': quizzes})

@login_required
def edit_quiz(request, quiz_id):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    teacher = Teacher.objects.get(user=request.user)
    
    if quiz.teacher != teacher:
        messages.error(request, 'Unauthorized')
        return redirect('quiz_management')
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title')
        quiz.subject_id = request.POST.get('subject')
        quiz.school_class_id = request.POST.get('class')
        quiz.start_time = request.POST.get('start_time')
        quiz.end_time = request.POST.get('end_time')
        quiz.duration_minutes = int(request.POST.get('duration_minutes', 60))
        quiz.instructions = request.POST.get('instructions', '')
        quiz.status = request.POST.get('status', 'draft')
        quiz.shuffle_questions = request.POST.get('shuffle_questions') == 'on'
        quiz.shuffle_options = request.POST.get('shuffle_options') == 'on'
        quiz.full_screen_mode = request.POST.get('full_screen_mode') == 'on'
        quiz.detect_tab_switching = request.POST.get('detect_tab_switching') == 'on'
        quiz.max_tab_switches = int(request.POST.get('max_tab_switches', 3))
        quiz.save()
        
        messages.success(request, 'Quiz updated successfully')
        return redirect('quiz_management')
    
    return render(request, 'teacher/edit_quiz.html', {
        'quiz': quiz,
        'subjects': teacher.subjects.all(),
        'classes': teacher.classes.all()
    })

@login_required
def quiz_results(request, quiz_id):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(quiz=quiz, is_submitted=True).select_related('student__user')
    
    return render(request, 'teacher/quiz_results.html', {
        'quiz': quiz,
        'attempts': attempts
    })

@login_required
def grade_theory(request, quiz_id):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    theory_questions = quiz.questions.filter(question_type='theory')
    
    if not theory_questions.exists():
        messages.info(request, 'This quiz has no theory questions')
        return redirect('quiz_management')
    
    attempts = QuizAttempt.objects.filter(quiz=quiz, is_submitted=True).prefetch_related('answers__question')
    
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        score = float(request.POST.get('score', 0))
        feedback = request.POST.get('feedback', '')
        
        answer = QuizAnswer.objects.get(id=answer_id)
        answer.manual_score = score
        answer.teacher_feedback = feedback
        answer.save()
        
        # Recalculate attempt scores
        attempt = answer.attempt
        
        # Calculate auto score from objective and multichoice questions
        auto_marks = 0
        for ans in attempt.answers.filter(question__question_type__in=['objective', 'multichoice'], is_correct=True):
            auto_marks += ans.question.max_marks
        attempt.auto_score = auto_marks
        
        # Calculate manual score from theory questions
        theory_score = attempt.answers.filter(question__question_type='theory').aggregate(total=models.Sum('manual_score'))['total'] or 0
        attempt.manual_score = theory_score
        
        # Calculate final score
        total_marks = quiz.questions.aggregate(total=models.Sum('max_marks'))['total'] or 1
        attempt.final_score = ((attempt.auto_score + attempt.manual_score) / total_marks) * 100
        
        # Check if all theory questions are graded
        ungraded = attempt.answers.filter(question__question_type='theory', manual_score=0).exists()
        attempt.is_graded = not ungraded
        attempt.save()
        
        messages.success(request, 'Score saved successfully')
        return redirect('grade_theory', quiz_id=quiz_id)
    
    # Prepare data for template
    attempts_data = []
    for attempt in attempts:
        theory_answers = []
        for question in theory_questions:
            try:
                answer = QuizAnswer.objects.get(attempt=attempt, question=question)
            except QuizAnswer.DoesNotExist:
                answer = QuizAnswer.objects.create(attempt=attempt, question=question)
            theory_answers.append({'question': question, 'answer': answer})
        attempts_data.append({'attempt': attempt, 'theory_answers': theory_answers})
    
    return render(request, 'teacher/grade_theory.html', {
        'quiz': quiz,
        'attempts_data': attempts_data
    })

@login_required
def delete_quiz(request, quiz_id):
    if request.method == 'DELETE':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        teacher = Teacher.objects.get(user=request.user)
        
        if quiz.teacher != teacher:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
        
        quiz.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def question_bank(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    from .forms import QuestionBankForm
    
    if request.method == 'POST':
        form = QuestionBankForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = teacher
            question.save()
            messages.success(request, 'Question added to bank')
            return redirect('question_bank')
    else:
        form = QuestionBankForm()
    
    questions = QuestionBank.objects.filter(subject__in=teacher.subjects.all())
    return render(request, 'teacher/question_bank.html', {
        'questions': questions,
        'subjects': teacher.subjects.all(),
        'form': form
    })

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        import os
        from django.conf import settings
        
        upload = request.FILES['upload']
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, upload.name)
        with open(file_path, 'wb+') as destination:
            for chunk in upload.chunks():
                destination.write(chunk)
        
        url = f"{settings.MEDIA_URL}uploads/{upload.name}"
        return JsonResponse({'uploaded': 1, 'fileName': upload.name, 'url': url})
    
    return JsonResponse({'uploaded': 0, 'error': {'message': 'Upload failed'}})

@login_required
def add_question_from_bank(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quiz_id')
            question_id = data.get('question_id')
            
            quiz = Quiz.objects.get(id=quiz_id)
            bank_question = QuestionBank.objects.get(id=question_id)
            
            Question.objects.create(
                quiz=quiz,
                question_type='objective',
                question_text=bank_question.question_text,
                option_a=bank_question.option_a,
                option_b=bank_question.option_b,
                option_c=bank_question.option_c,
                option_d=bank_question.option_d,
                correct_answer=bank_question.correct_answer,
                max_marks=1
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
def edit_question(request, question_id):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    question = get_object_or_404(Question, id=question_id)
    from .forms import QuestionForm
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated')
            return redirect('add_questions', quiz_id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'teacher/edit_question.html', {
        'question': question,
        'form': form
    })

@login_required
def delete_question(request, question_id):
    if request.method == 'DELETE':
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def add_questions(request, quiz_id):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    from .forms import QuestionForm
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.question_type = request.POST.get('question_type', 'objective')
            question.max_marks = int(request.POST.get('max_marks', 1))
            
            # Handle multichoice correct answers
            if question.question_type == 'multichoice':
                correct_multi = request.POST.getlist('correct_multi')
                question.correct_answer = ','.join(sorted(correct_multi))
            
            question.save()
            messages.success(request, 'Question added')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    questions = quiz.questions.all()
    return render(request, 'teacher/add_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'form': form
    })

@login_required
def class_broadsheet(request):
    teacher = Teacher.objects.get(user=request.user)
    try:
        class_teacher = ClassTeacher.objects.get(teacher=teacher)
    except ClassTeacher.DoesNotExist:
        return redirect('dashboard')
    
    students = Student.objects.filter(school_class=class_teacher.school_class)
    subjects = Subject.objects.all()
    active_term = Term.objects.filter(is_active=True).first()
    
    broadsheet_data = []
    for student in students:
        student_results = {}
        total_score = 0
        subject_count = 0
        
        for subject in subjects:
            try:
                result = Result.objects.get(
                    student=student, 
                    subject=subject, 
                    term=active_term
                )
                student_results[subject.code] = {
                    'total': result.total_score,
                    'grade': result.grade
                }
                total_score += float(result.total_score)
                subject_count += 1
            except Result.DoesNotExist:
                student_results[subject.code] = {'total': '-', 'grade': '-'}
        
        average = total_score / subject_count if subject_count > 0 else 0
        
        broadsheet_data.append({
            'student': student,
            'results': student_results,
            'average': round(average, 2)
        })
    
    return render(request, 'class_teacher/broadsheet.html', {
        'broadsheet_data': broadsheet_data,
        'subjects': subjects,
        'class_name': class_teacher.school_class.name,
        'term': active_term
    })


@login_required
def manage_attendance(request):
    """Allow class teachers to record attendance and result comments for their students."""
    teacher = Teacher.objects.get(user=request.user)
    try:
        class_teacher = ClassTeacher.objects.get(teacher=teacher)
    except ClassTeacher.DoesNotExist:
        return redirect('dashboard')

    students = Student.objects.filter(school_class=class_teacher.school_class).select_related('user')
    active_term = Term.objects.filter(is_active=True).first()

    if not active_term:
        messages.error(request, 'No active term is set. Please contact the administrator.')
        return redirect('dashboard')

    if request.method == 'POST':
        for student in students:
            total_days_str = request.POST.get(f'attendance_{student.id}_total_days', '').strip()
            present_days_str = request.POST.get(f'attendance_{student.id}_days_present', '').strip()
            teacher_comment = request.POST.get(f'comment_{student.id}', '').strip()

            # Save attendance if any value is provided
            if total_days_str or present_days_str:
                try:
                    total_days = int(total_days_str or 0)
                    days_present = int(present_days_str or 0)
                except ValueError:
                    continue

                days_absent = max(total_days - days_present, 0)
                Attendance.objects.update_or_create(
                    student=student,
                    term=active_term,
                    defaults={
                        'total_days': total_days,
                        'days_present': days_present,
                        'days_absent': days_absent,
                    }
                )

            # Save teacher comment (create record even if comment is empty but previously existed)
            if teacher_comment or Comment.objects.filter(student=student, term=active_term).exists():
                Comment.objects.update_or_create(
                    student=student,
                    term=active_term,
                    defaults={
                        'teacher_comment': teacher_comment,
                    }
                )

        messages.success(request, 'Attendance and comments updated successfully.')
        return redirect('manage_attendance')

    # Preload existing attendance and comments for display
    attendance_qs = Attendance.objects.filter(student__in=students, term=active_term)
    comment_qs = Comment.objects.filter(student__in=students, term=active_term)

    attendance_map = {att.student.id: att for att in attendance_qs}
    comment_map = {com.student.id: com for com in comment_qs}

    return render(request, 'class_teacher/manage_attendance.html', {
        'teacher': teacher,
        'class_teacher': class_teacher,
        'students': students,
        'term': active_term,
        'attendance_map': attendance_map,
        'comment_map': comment_map,
    })

@login_required
def results_overview(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'teacher/results_overview.html', {
        'classes': teacher.classes.all(),
        'subjects': teacher.subjects.all(),
    })

@login_required
def component_results(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'teacher/component_results.html', {
        'classes': teacher.classes.all(),
        'subjects': teacher.subjects.all(),
        'active_term': Term.objects.filter(is_active=True).first()
    })

@login_required
def get_components(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    
    if class_id and subject_id:
        components = ResultComponent.objects.filter(
            school_class_id=class_id,
            subject_id=subject_id
        ).values('id', 'component_name', 'weight', 'max_score')
        
        return JsonResponse({'components': list(components)})
    
    return JsonResponse({'components': []})

@login_required
def get_student_results(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    term_id = request.GET.get('term_id')
    
    if class_id and subject_id and term_id:
        students = Student.objects.filter(school_class_id=class_id)
        student_data = []
        
        for student in students:
            # Get component scores
            component_scores = {}
            components = ResultComponent.objects.filter(
                school_class_id=class_id,
                subject_id=subject_id
            )
            
            for component in components:
                try:
                    comp_result = ComponentResult.objects.get(
                        student=student,
                        component=component,
                        term_id=term_id
                    )
                    component_scores[component.id] = float(comp_result.score)
                except ComponentResult.DoesNotExist:
                    component_scores[component.id] = None
            
            # Get final result
            try:
                result = Result.objects.get(
                    student=student,
                    subject_id=subject_id,
                    term_id=term_id
                )
                total_score = float(result.total_score)
                grade = result.grade
            except Result.DoesNotExist:
                total_score = None
                grade = None
            
            student_data.append({
                'id': student.id,
                'name': student.user.get_full_name(),
                'student_id': student.student_id,
                'component_scores': component_scores,
                'total_score': total_score,
                'grade': grade
            })
        
        return JsonResponse({'students': student_data})
    
    return JsonResponse({'students': []})

@login_required
def update_component_score(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        
        student_id = data.get('student_id')
        component_id = data.get('component_id')
        term_id = data.get('term_id')
        score = data.get('score')
        
        try:
            student = Student.objects.get(id=student_id)
            component = ResultComponent.objects.get(id=component_id)
            term = Term.objects.get(id=term_id)
            
            # Verify teacher can manage this
            teacher = Teacher.objects.get(user=request.user)
            if (component.subject not in teacher.subjects.all() or 
                student.school_class not in teacher.classes.all()):
                return JsonResponse({'success': False, 'message': 'Unauthorized'})
            
            # Update component result
            comp_result, created = ComponentResult.objects.update_or_create(
                student=student,
                component=component,
                term=term,
                defaults={'score': score}
            )
            
            # Recalculate final result
            result, created = Result.objects.get_or_create(
                student=student,
                subject=component.subject,
                term=term
            )
            result.calculate_total()
            
            return JsonResponse({
                'success': True,
                'total_score': float(result.total_score),
                'grade': result.grade
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def student_promotion(request):
    teacher = Teacher.objects.get(user=request.user)
    try:
        class_teacher = ClassTeacher.objects.get(teacher=teacher)
    except ClassTeacher.DoesNotExist:
        return redirect('dashboard')
    
    students = Student.objects.filter(school_class=class_teacher.school_class)
    
    # Calculate promotion eligibility
    students_data = []
    eligible_count = 0
    not_eligible_count = 0
    promoted_count = 0
    
    active_term = Term.objects.filter(is_active=True).first()
    
    for student in students:
        # Calculate average and failures
        results = Result.objects.filter(student=student, term=active_term)
        
        if results.exists():
            total_score = sum(float(r.total_score) for r in results)
            average = total_score / results.count()
            failures = results.filter(total_score__lt=50).count()
        else:
            average = 0
            failures = 0
        
        # Mock attendance (in real system, get from attendance records)
        attendance = 85  # Default attendance percentage
        
        # Check eligibility
        eligible = (average >= 50 and failures <= 2 and attendance >= 75)
        
        if student.is_promoted:
            promoted_count += 1
        elif eligible:
            eligible_count += 1
        else:
            not_eligible_count += 1
        
        students_data.append({
            'student': student,
            'average': average,
            'failures': failures,
            'attendance': attendance,
            'eligible': eligible
        })
    
    # Get available classes for promotion
    available_classes = SchoolClass.objects.exclude(id=class_teacher.school_class.id)
    
    return render(request, 'class_teacher/student_promotion.html', {
        'class_teacher': class_teacher,
        'students_data': students_data,
        'available_classes': available_classes,
        'eligible_count': eligible_count,
        'not_eligible_count': not_eligible_count,
        'promoted_count': promoted_count,
        'total_students': students.count()
    })

@login_required
def promote_students(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        student_ids = data.get('student_ids', [])
        target_class_id = data.get('target_class_id')
        force_promote = data.get('force_promote', False)
        
        try:
            target_class = SchoolClass.objects.get(id=target_class_id)
            
            for student_id in student_ids:
                student = Student.objects.get(id=student_id)
                student.is_promoted = True
                student.promoted_to = target_class
                student.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'{len(student_ids)} students promoted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False})

@login_required
def view_analytics(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(user=request.user)
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    
    if class_id and subject_id:
        results = Result.objects.filter(
            student__school_class_id=class_id,
            subject_id=subject_id
        )
        
        total_students = results.values('student').distinct().count()
        avg_score = results.aggregate(Avg('total_score'))['total_score__avg'] or 0
        pass_count = results.filter(total_score__gte=50).count()
        fail_count = results.filter(total_score__lt=50).count()
        
        grade_distribution = []
        for grade in ['A+', 'A', 'B', 'C', 'D', 'F']:
            count = results.filter(grade=grade).count()
            percentage = (count * 100 / total_students) if total_students > 0 else 0
            grade_distribution.append({'grade': grade, 'count': count, 'percentage': percentage})
        
        context = {
            'school_class': SchoolClass.objects.get(id=class_id),
            'subject': Subject.objects.get(id=subject_id),
            'total_students': total_students,
            'avg_score': avg_score,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'grade_distribution': grade_distribution,
            'has_data': True,
        }
    else:
        context = {
            'classes': teacher.classes.all(),
            'subjects': teacher.subjects.all(),
        }
    
    return render(request, 'teacher/analytics.html', context)

@login_required
def export_results(request):
    if request.user.role != 'subject_teacher':
        return redirect('dashboard')
    
    import csv
    from django.http import HttpResponse
    
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    
    if not class_id or not subject_id:
        messages.error(request, 'Please select class and subject')
        return redirect('results_overview')
    
    school_class = SchoolClass.objects.get(id=class_id)
    subject = Subject.objects.get(id=subject_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{school_class.name}_{subject.code}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Total Score', 'Grade', 'Grade Point', 'Remark'])
    
    results = Result.objects.filter(
        student__school_class=school_class,
        subject=subject
    ).select_related('student__user')
    
    for result in results:
        writer.writerow([
            result.student.student_id,
            result.student.user.get_full_name(),
            result.total_score,
            result.grade,
            result.grade_point,
            result.remark
        ])
    
    return response

@login_required
def view_quiz_result(request, quiz_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = Student.objects.get(user=request.user)
    attempt = get_object_or_404(QuizAttempt, quiz=quiz, student=student, is_submitted=True)
    
    questions = quiz.questions.all()
    results = []
    
    for question in questions:
        try:
            answer = QuizAnswer.objects.get(attempt=attempt, question=question)
            user_answer = answer.selected_answer if question.question_type in ['objective', 'multichoice'] else answer.theory_answer
            user_answers_list = user_answer.split(',') if user_answer else []
            correct_answers_list = question.correct_answer.split(',') if question.correct_answer else []
            
            results.append({
                'question': question,
                'user_answer': user_answer,
                'user_answers_list': user_answers_list,
                'correct_answers_list': correct_answers_list,
                'is_correct': answer.is_correct,
                'manual_score': answer.manual_score,
                'feedback': answer.teacher_feedback
            })
        except QuizAnswer.DoesNotExist:
            results.append({
                'question': question,
                'user_answer': None,
                'user_answers_list': [],
                'correct_answers_list': question.correct_answer.split(',') if question.correct_answer else [],
                'is_correct': False,
                'manual_score': 0,
                'feedback': ''
            })
    
    return render(request, 'student/view_quiz_result.html', {
        'quiz': quiz,
        'attempt': attempt,
        'results': results
    })

@login_required
def generate_tokens(request):
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        term_id = request.POST.get('term_id')
        max_uses = int(request.POST.get('max_uses', 3))
        
        term = Term.objects.get(id=term_id)
        students = Student.objects.all()
        
        for student in students:
            ResultToken.objects.get_or_create(
                student=student,
                term=term,
                defaults={'max_uses': max_uses}
            )
        
        messages.success(request, f'Tokens generated for {students.count()} students')
        return redirect('generate_tokens')
    
    terms = Term.objects.all()
    tokens = ResultToken.objects.select_related('student__user', 'student__school_class', 'term').order_by('-created_at')
    return render(request, 'admin/generate_tokens.html', {'terms': terms, 'tokens': tokens})

def check_result(request):
    if request.method == 'POST':
        token = request.POST.get('token', '').strip().upper()
        
        try:
            result_token = ResultToken.objects.get(token=token)
            
            if not result_token.can_use():
                messages.error(request, 'Token usage limit exceeded')
                return redirect('check_result')
            
            result_token.use_token()
            return redirect('view_result_card', token=token)
            
        except ResultToken.DoesNotExist:
            messages.error(request, 'Invalid token')
    
    return render(request, 'check_result.html')

def view_result_card(request, token):
    result_token = get_object_or_404(ResultToken, token=token)
    student = result_token.student
    term = result_token.term
    
    results = Result.objects.filter(student=student, term=term).select_related('subject')
    
    # Overall totals/averages for this student
    total_score = sum(float(r.total_score) for r in results)
    total_subjects = results.count()
    average = total_score / total_subjects if total_subjects > 0 else 0
    overall_percentage = average
    
    # Derive overall grade/remark from grading system
    overall_grade = None
    overall_remark = ''
    grading = GradingSystem.objects.filter(
        min_score__lte=average,
        max_score__gte=average
    ).first()
    if grading:
        overall_grade = grading.grade
        overall_remark = grading.remark
    
    # Batch/class ranking statistics
    from django.db.models import Avg as AvgFunc
    class_results = Result.objects.filter(
        student__school_class=student.school_class,
        term=term
    ).values('student').annotate(avg=AvgFunc('total_score')).order_by('-avg')
    
    position = 1
    class_highest = 0
    class_lowest = 0
    class_average = 0
    
    if class_results:
        # Determine this student's position
        for idx, cr in enumerate(class_results, 1):
            if cr['student'] == student.id:
                position = idx
                break
        
        avg_values = [float(cr['avg']) for cr in class_results]
        class_highest = max(avg_values)
        class_lowest = min(avg_values)
        class_average = sum(avg_values) / len(avg_values)
    
    attendance = Attendance.objects.filter(student=student, term=term).first()
    comment = Comment.objects.filter(student=student, term=term).first()
    psychomotor = Psychomotor.objects.filter(student=student, term=term).first()
    effective_domain = EffectiveDomain.objects.filter(student=student, term=term).first()
    school_settings = SchoolSettings.objects.first()
    total_students = Student.objects.filter(school_class=student.school_class).count()
    
    context = {
        'student': student,
        'term': term,
        'results': results,
        'average': average,
        'total_score': total_score,
        'overall_percentage': overall_percentage,
        'overall_grade': overall_grade,
        'overall_remark': overall_remark,
        'position': position,
        'total_students': total_students,
        'class_highest': class_highest,
        'class_lowest': class_lowest,
        'class_average': class_average,
        'attendance': attendance,
        'comment': comment,
        'psychomotor': psychomotor,
        'effective_domain': effective_domain,
        'school_settings': school_settings,
    }
    
    return render(request, 'result_card.html', context)

@login_required
def revert_promotion(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        
        try:
            student = Student.objects.get(id=student_id)
            student.is_promoted = False
            student.promoted_to = None
            student.save()
            
            return JsonResponse({'success': True, 'message': 'Promotion reverted successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False})

@login_required
def enhanced_quiz(request, quiz_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = Student.objects.get(user=request.user)
    
    if not quiz.is_live():
        messages.error(request, 'Quiz is not currently available')
        return redirect('dashboard')
    
    attempt, created = QuizAttempt.objects.get_or_create(
        quiz=quiz, student=student,
        defaults={'start_time': timezone.now()}
    )
    
    if attempt.is_submitted:
        return redirect('view_quiz_result', quiz_id=quiz_id)
    
    questions = list(quiz.questions.all())
    
    # Shuffle questions if enabled
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)
    
    if request.method == 'POST':
        # Process submission
        auto_score = 0
        total_objective_marks = 0
        
        for question in questions:
            if question.question_type == 'objective':
                answer = request.POST.get(f'question_{question.id}')
                if answer:
                    quiz_answer, created = QuizAnswer.objects.update_or_create(
                        attempt=attempt, question=question,
                        defaults={'selected_answer': answer}
                    )
                    if quiz_answer.is_correct:
                        auto_score += question.max_marks
                total_objective_marks += question.max_marks
            
            elif question.question_type == 'multichoice':
                answers = request.POST.getlist(f'question_{question.id}')
                selected = ','.join(sorted(answers)) if answers else ''
                quiz_answer, created = QuizAnswer.objects.update_or_create(
                    attempt=attempt, question=question,
                    defaults={'selected_answer': selected}
                )
                if quiz_answer.is_correct:
                    auto_score += question.max_marks
                total_objective_marks += question.max_marks
            
            elif question.question_type == 'theory':
                theory_answer = request.POST.get(f'theory_{question.id}')
                if theory_answer:
                    QuizAnswer.objects.update_or_create(
                        attempt=attempt, question=question,
                        defaults={'theory_answer': theory_answer}
                    )
        
        # Update attempt
        attempt.end_time = timezone.now()
        attempt.is_submitted = True
        attempt.auto_score = auto_score
        
        # Check if all questions are auto-graded (objective/multichoice)
        theory_questions = [q for q in questions if q.question_type == 'theory']
        total_marks = sum(q.max_marks for q in questions)
        
        if not theory_questions:
            attempt.final_score = (auto_score / total_marks * 100) if total_marks > 0 else 0
            attempt.is_graded = True
        
        attempt.save()
        
        # Log auto-submit reason if present
        auto_submit_reason = request.POST.get('auto_submit_reason')
        if auto_submit_reason:
            attempt.add_integrity_event('auto_submit', auto_submit_reason)
        
        if theory_questions:
            messages.success(request, f'Quiz submitted! Objective score: {auto_score}/{total_objective_marks}. Theory questions pending review.')
        else:
            messages.success(request, f'Quiz submitted! Your score: {auto_score}/{total_objective_marks}')
        
        return redirect('dashboard')
    
    return render(request, 'student/enhanced_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'attempt': attempt
    })
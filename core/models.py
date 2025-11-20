from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from ckeditor.fields import RichTextField
import json
import secrets

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('subject_teacher', 'Subject Teacher'),
        ('class_teacher', 'Class Teacher'),
        ('super_admin', 'Super Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)

class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    stream = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'stream']

    def __str__(self):
        return f"{self.name} {self.stream}".strip()

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    pass_mark = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GradingSystem(models.Model):
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    grade = models.CharField(max_length=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    remark = models.CharField(max_length=50)

    class Meta:
        ordering = ['-min_score']

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"

class QuestionBank(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question_text = RichTextField()
    option_a = RichTextField()
    option_b = RichTextField()
    option_c = RichTextField()
    option_d = RichTextField()
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium')
    created_by = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.code} - {self.question_text[:50]}"

class ResultComponent(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    component_name = models.CharField(max_length=50)
    weight = models.IntegerField()
    max_score = models.IntegerField(default=100)
    linked_quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ['school_class', 'subject', 'component_name']

    def __str__(self):
        return f"{self.school_class} - {self.subject} - {self.component_name} ({self.weight}%)"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    address = models.TextField(blank=True)
    passport_photo = models.ImageField(upload_to='students/', blank=True)
    is_promoted = models.BooleanField(default=False)
    promoted_to = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='promoted_students')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField(Subject, blank=True)
    classes = models.ManyToManyField(SchoolClass, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

class ClassTeacher(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    school_class = models.OneToOneField(SchoolClass, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.school_class.name}"

class Term(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    result_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ResultToken(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    token = models.CharField(max_length=20, unique=True)
    max_uses = models.IntegerField(default=3)
    uses_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'term']
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(12)[:12].upper()
        super().save(*args, **kwargs)
    
    def can_use(self):
        return self.uses_count < self.max_uses
    
    def use_token(self):
        if self.can_use():
            self.uses_count += 1
            self.save()
            return True
        return False

class Attendance(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    total_days = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['student', 'term']
    
    def percentage(self):
        if self.total_days > 0:
            return (self.days_present / self.total_days) * 100
        return 0

class Comment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    teacher_comment = models.TextField(blank=True)
    proprietor_comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'term']


class Psychomotor(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    sports_games = models.CharField(max_length=5, blank=True)
    handwriting = models.CharField(max_length=5, blank=True)
    drawing_painting = models.CharField(max_length=5, blank=True)
    crafts = models.CharField(max_length=5, blank=True)
    music_drama = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ['student', 'term']
        verbose_name = 'Psychomotor'
        verbose_name_plural = 'Psychomotor'

    def __str__(self):
        return f"Psychomotor - {self.student} - {self.term}"


class EffectiveDomain(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    punctuality = models.CharField(max_length=5, blank=True)
    neatness = models.CharField(max_length=5, blank=True)
    attentiveness = models.CharField(max_length=5, blank=True)
    politeness = models.CharField(max_length=5, blank=True)
    relationship_with_others = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ['student', 'term']
        verbose_name = 'Effective Domain'
        verbose_name_plural = 'Effective Domains'

    def __str__(self):
        return f"Effective Domain - {self.student} - {self.term}"


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200)
    school_address = models.TextField()
    school_logo = models.ImageField(upload_to='school/', blank=True)
    school_seal = models.ImageField(upload_to='school/', blank=True)
    principal_signature = models.ImageField(upload_to='school/', blank=True)
    principal_name = models.CharField(max_length=100)
    proprietor_name = models.CharField(max_length=100, blank=True)
    school_motto = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name_plural = 'School Settings'
    
    def __str__(self):
        return self.school_name

class ComponentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    component = models.ForeignKey(ResultComponent, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'component', 'term']

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    remark = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'term']

    def calculate_total(self):
        components = ComponentResult.objects.filter(
            student=self.student,
            component__subject=self.subject,
            component__school_class=self.student.school_class,
            term=self.term
        )
        
        total = 0
        for comp_result in components:
            weighted_score = (comp_result.score / comp_result.component.max_score) * comp_result.component.weight
            total += weighted_score
        
        self.total_score = total
        
        grading = GradingSystem.objects.filter(
            min_score__lte=total,
            max_score__gte=total
        ).first()
        
        if grading:
            self.grade = grading.grade
            self.grade_point = grading.grade_point
            self.remark = grading.remark
        
        self.save()

class Quiz(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    instructions = models.TextField(blank=True)
    shuffle_questions = models.BooleanField(default=True)
    shuffle_options = models.BooleanField(default=True)
    full_screen_mode = models.BooleanField(default=True)
    detect_tab_switching = models.BooleanField(default=True)
    max_tab_switches = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.school_class.name}"

    def is_live(self):
        now = timezone.now()
        return self.status == 'live' or (self.status == 'scheduled' and self.start_time <= now <= self.end_time)

class Question(models.Model):
    QUESTION_TYPES = [
        ('objective', 'Objective'),
        ('multichoice', 'Multi-Choice'),
        ('theory', 'Theory'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='objective')
    question_text = RichTextField()
    option_a = RichTextField(blank=True)
    option_b = RichTextField(blank=True)
    option_c = RichTextField(blank=True)
    option_d = RichTextField(blank=True)
    correct_answer = models.CharField(max_length=10, blank=True)  # Can store 'A,B,C' for multichoice
    max_marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.id}"

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    auto_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    manual_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_submitted = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    integrity_log = models.TextField(default='[]')
    tab_switches = models.IntegerField(default=0)

    class Meta:
        unique_together = ['quiz', 'student']

    def add_integrity_event(self, event_type, details=''):
        log = json.loads(self.integrity_log)
        log.append({
            'timestamp': timezone.now().isoformat(),
            'event': event_type,
            'details': details
        })
        self.integrity_log = json.dumps(log)
        
        if event_type == 'tab_switch':
            self.tab_switches += 1
        
        self.save()

class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=10, blank=True)  # Can store 'A,B,C' for multichoice
    theory_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    manual_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    teacher_feedback = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.question.question_type in ['objective', 'multichoice'] and self.selected_answer:
            if self.question.question_type == 'multichoice':
                # For multichoice, check if selected answers match correct answers
                selected = set(self.selected_answer.split(','))
                correct = set(self.question.correct_answer.split(','))
                self.is_correct = selected == correct
            else:
                self.is_correct = self.selected_answer == self.question.correct_answer
        super().save(*args, **kwargs)
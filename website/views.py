from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import NewsPost, GalleryImage, NewsletterSubscriber
from core.models import Student, Teacher

def home(request):
    posts = NewsPost.objects.filter(published=True)[:3]
    post_highlights = posts[:3]
    gallery_images = list(GalleryImage.objects.all()[:12])
    
    # Get upcoming birthdays from students
    today = timezone.now().date()
    upcoming_birthdays = []
    
    students = Student.objects.select_related('user', 'school_class').all()
    for student in students:
        if student.date_of_birth:
            birthday_this_year = student.date_of_birth.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            days_until = (birthday_this_year - today).days
            if 0 <= days_until <= 30:
                upcoming_birthdays.append({
                    'name': student.user.get_full_name(),
                    'date': birthday_this_year,
                    'days_until': days_until,
                    'class': student.school_class.name
                })
    
    upcoming_birthdays.sort(key=lambda x: x['days_until'])
    upcoming_birthdays = upcoming_birthdays[:5]
    
    return render(request, 'website/home.html', {
        'posts': posts,
        'post_highlights': post_highlights,
        'gallery_images': gallery_images,
        'upcoming_birthdays': upcoming_birthdays,
    })

def about(request):
    return render(request, 'website/about.html')

def admissions(request):
    from .models import Faq, DownloadableForm
    faqs = Faq.objects.filter(published=True).order_by('order')
    forms = DownloadableForm.objects.filter(active=True).order_by('order')
    return render(request, 'website/admissions.html', {
        'faqs': faqs,
        'forms': forms,
    })

def academics(request):
    return render(request, 'website/academics.html')

@require_POST
def admissions_inquiry(request):
    from django.conf import settings
    from django.core.mail import mail_admins
    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    message = (request.POST.get('message') or '').strip()
    if not (name and email and message):
        messages.error(request, 'Please fill in your name, email and message.')
        return redirect('website:admissions')
    from .models import Inquiry
    Inquiry.objects.create(name=name, email=email, message=message)
    try:
        mail_admins(subject='New Admissions Inquiry', message=f'From: {name} <{email}>\n\n{message}', fail_silently=True)
    except Exception:
        pass
    messages.success(request, 'Your inquiry has been received. We will get back to you shortly.')
    return redirect('website:admissions')

@require_POST
def newsletter_subscribe(request):
    email = (request.POST.get('email') or '').strip().lower()
    name = (request.POST.get('name') or '').strip()
    if not email:
        messages.error(request, 'Please provide a valid email address.')
        return redirect('website:home')
    sub, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={'full_name': name})
    if not created and name and sub.full_name != name:
        sub.full_name = name
        sub.save()
    messages.success(request, 'Subscribed successfully!')
    return redirect('website:home')

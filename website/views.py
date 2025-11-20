from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import NewsPost, GalleryImage, NewsletterSubscriber

def home(request):
    posts = NewsPost.objects.filter(published=True)[:3]
    post_highlights = posts[:3]
    gallery_images = list(GalleryImage.objects.all()[:12])
    return render(request, 'website/home.html', {
        'posts': posts,
        'post_highlights': post_highlights,
        'gallery_images': gallery_images,
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
    # Notify admins if configured
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

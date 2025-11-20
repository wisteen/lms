from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mass_mail
from .models import NewsPost, GalleryImage, NewsletterSubscriber, NewsletterIssue, Faq, DownloadableForm, Inquiry

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "created_at")
    list_filter = ("published", "created_at")
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("thumb", "caption", "is_featured", "order", "created_at")
    list_editable = ("is_featured", "order")

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;object-fit:cover;"/>', obj.image.url)
        return "-"

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email", "full_name")

@admin.action(description="Send this issue to all active subscribers")
def send_issue(modeladmin, request, queryset):
    for issue in queryset:
        subs = NewsletterSubscriber.objects.filter(is_active=True).values_list("email", flat=True)
        if not subs:
            continue
        subject = issue.title
        # Strip basic HTML for plain-text fallback
        from django.utils.html import strip_tags
        message_plain = strip_tags(issue.body)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
        datatuple = [(subject, message_plain, from_email, [email]) for email in subs]
        send_mass_mail(datatuple, fail_silently=True)
        issue.sent = True
        issue.sent_at = timezone.now()
        issue.save()

@admin.register(NewsletterIssue)
class NewsletterIssueAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "sent", "sent_at")
    actions = [send_issue]

@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "published", "order", "created_at")
    list_editable = ("published", "order")
    search_fields = ("question",)

@admin.register(DownloadableForm)
class DownloadableFormAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "order", "created_at")
    list_editable = ("active", "order")
    search_fields = ("title", "description")

@admin.action(description="Mark selected inquiries as processed")
def mark_processed(modeladmin, request, queryset):
    queryset.update(processed=True)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "processed", "created_at")
    list_filter = ("processed", "created_at")
    search_fields = ("name", "email", "message")
    actions = [mark_processed]

# Register your models here.

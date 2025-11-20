from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'core',
    'website',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_management.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'extraPlugins': 'mathjax',
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS_HTML',
        'height': 150,
    },
}

JAZZMIN_SETTINGS = {
    'site_title': 'DGLHS Admin',
    'site_header': 'DGLHS Admin',
    'site_brand': 'Dan-GraciousLand',
    'site_logo': '/img/logo.png',
    'site_icon': '/img/logo.png',
    'login_logo': '/img/logo.png',
    'login_logo_dark': '/img/logo.png',
    'site_logo_classes': 'img-circle',
    'welcome_sign': 'Welcome to Dan-Gracious Land High School Admin',
    'copyright': 'Dan-Gracious Land High School',
    'search_model': ['auth.User', 'core.Student', 'core.Teacher', 'core.Subject', 'core.SchoolClass'],
    'topmenu_links': [
        {'name': 'Admin Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'Generate Tokens', 'url': 'generate_tokens', 'permissions': ['auth.view_user']},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.group': 'fas fa-user-friends',
        # Core app models
        'core.User': 'fas fa-user-shield',
        'core.Student': 'fas fa-user-graduate',
        'core.Teacher': 'fas fa-chalkboard-teacher',
        'core.ClassTeacher': 'fas fa-user-tie',
        'core.SchoolClass': 'fas fa-school',
        'core.Subject': 'fas fa-book-open',
        'core.GradingSystem': 'fas fa-sliders-h',
        'core.Term': 'fas fa-calendar-alt',
        'core.SchoolSettings': 'fas fa-cogs',
        'core.ResultComponent': 'fas fa-puzzle-piece',
        'core.ComponentResult': 'fas fa-check-square',
        'core.Result': 'fas fa-poll',
        'core.ResultToken': 'fas fa-key',
        'core.Attendance': 'fas fa-calendar-check',
        'core.Comment': 'fas fa-comment',
        'core.Psychomotor': 'fas fa-running',
        'core.EffectiveDomain': 'fas fa-star-half-alt',
        'core.QuestionBank': 'fas fa-database',
        'core.Quiz': 'fas fa-question-circle',
        'core.Question': 'fas fa-question',
        'core.QuizAttempt': 'fas fa-clipboard-check',
        'core.QuizAnswer': 'fas fa-check-double',
        # Website models
        'website.NewsPost': 'fas fa-newspaper',
        'website.GalleryImage': 'fas fa-images',
        'website.NewsletterSubscriber': 'fas fa-envelope-open-text',
        'website.NewsletterIssue': 'fas fa-paper-plane',
        'website.Faq': 'fas fa-question',
        'website.DownloadableForm': 'fas fa-file-download',
        'website.Inquiry': 'fas fa-inbox',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': False,
    'custom_css': None,
    'custom_js': None,
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {'auth.user': 'collapsible', 'auth.group': 'vertical_tabs'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

AUTH_USER_MODEL = 'core.User'
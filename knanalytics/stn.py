"""
Django settings for knanalytics project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

LAUNCH_METHOD = 'POST'
LAUNCH_URL = 'https://pe-xl-dev.knowdl.com/econservice/econlaunch/toolLaunch/'
XLSIMS_LAUNCH_URL = 'https://pe-xl-dev.knowdl.com/xlsim/simLaunch/launch/'
TPI_SHARED_SECRET = "test"
APP_REDIRECT_URL = "https://pe-xl-dev.knowdl.com/app"     # please to exclude trailing slash!!!
APP_REDIRECT_URL_CA = "https://pe-xl-dev.knowdl.com/ca/"
APP_REDIRECT_URL_UE = "https://pe-xl-dev.knowdl.com/unemployment/"
APP_REDIRECT_SETTINGS_URL_CA = "https://pe-xl-dev.knowdl.com/ca/settings.html"
APP_REDIRECT_SETTINGS_URL_UE = "https://pe-xl-dev.knowdl.com/unemployment/settings.html"
SIMS_EMULATOR_ROOT = '/atm_sims/simsEmulator/'
SIMS_ROOT = '/atm_sims/'

DATA_URI = ''
BYPASS_OAUTH = False
COURSE_REVIEW_LAUNCH_TABLE = {
    'unemployment': 'https://pe-xl-dev.knowdl.com/unemployment/classReview.html',
    'comparative_advantage': 'https://pe-xl-dev.knowdl.com/ca/classReview.html',
    'inflation': 'https://pe-xl-dev.knowdl.com/inflation/classReview.html',
    'opportunity_cost': 'https://pe-xl-dev.knowdl.com/oppcost/classReview.html',
    'monetary_policy': 'https://pe-xl-dev.knowdl.com/monetarypolicy/classReview.html',
    }

ECON_LAUNCH_TABLE = {
    'unemployment': 'https://pe-xl-dev.knowdl.com/unemployment/',
    'comparative_advantage': 'https://pe-xl-dev.knowdl.com/ca/',
    'inflation': 'https://pe-xl-dev.knowdl.com/inflation/',
    'opportunity_cost': 'https://pe-xl-dev.knowdl.com/oppcost/',
    'monetary_policy': 'https://pe-xl-dev.knowdl.com/monetarypolicy/',
    }

ECON_SETTINGS_LAUNCH_TABLE = {
    'unemployment': 'https://pe-xl-dev.knowdl.com/unemployment/settings.html',
    'comparative_advantage': 'https://pe-xl-dev.knowdl.com/ca/settings.html',
    'inflation': 'https://pe-xl-dev.knowdl.com/inflation/settings.html',
    'opportunity_cost': 'https://pe-xl-dev.knowdl.com/oppcost/settings.html',    
    'monetary_policy': 'https://pe-xl-dev.knowdl.com/monetarypolicy/settings.html',
    }

OUTCOMES_URL = 'http://cert.isb.lift.pearsoncmg.com/v1/dataexchange/tpi/submit'
OUTCOMES_USER = 'appuser'
OUTCOMES_PW = 'appuser1'
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'econservice',
		'USER': 'root',
		'PASSWORD': 'Kn0wdl!23',
		'HOST': '172.16.1.149',
		'PORT': '3306',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

ROOT_PATH = os.path.dirname(__file__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

STATIC_ROOT = os.path.join(ROOT_PATH, 'staticfiles')

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^3s2k$xhx&-h^^rq1#5wp6!y$4x7_0yy8qi!53%yiinc^v-2f%'

ALLOWED_HOSTS = ['*']

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'knanalytics.urls'

WSGI_APPLICATION = 'knanalytics.wsgi.application'
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gldata',
    #'econ.ca',
    #'econ.ue',
    #'econ.inflation',
    'gllaunch',
    'datacapture',
    'xlsims',
    #'econ.monetary_policy', 
    #'econ.common_services',
    #'econ.gdp',
    'knowdlsim',
    'knowdlsim.templatetags',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOG_DIR = os.path.dirname(__file__)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },     
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'fredinfo':{
             'level':'INFO',
             'class':'logging.FileHandler',
             'filename':LOG_DIR+'/fred.log',
             'formatter': 'verbose',
        },        
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'fred_ue':{
            'handlers':['fredinfo'],
            'level':'INFO',
            'propagate':True,
        },
        'fred_inflation':{
            'handlers':['fredinfo'],
            'level':'INFO',
            'propagate':True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'glservice_cache',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

FRED_API_KEY = '1c3266c33784d3a4a4b7875a34ae2364'
FRED_API_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations?api_key=%s&file_type=json&observation_start=1960-01-01' % FRED_API_KEY


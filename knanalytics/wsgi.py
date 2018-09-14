"""
WSGI config for knanalytics project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append("/opt/data/app1/knanalytics")

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "knanalytics.settings"

application = get_wsgi_application()

#import knanalytics.monitor
#knanalytics.monitor.start(interval=1.0)


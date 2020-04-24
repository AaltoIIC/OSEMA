"""
WSGI config for sensor_management_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""
import os
import sys


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sensor_management_platform.settings")

sys.path.append('/home/pi/apache_server/sensor-management-platform')
sys.path.append('/home/pi/apache_server/sensor-management-platform/sensor_management_platform')


application = get_wsgi_application()


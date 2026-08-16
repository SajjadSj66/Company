import sys
import os

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(__file__))

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company.settings')

application = get_wsgi_application()
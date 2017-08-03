#coding=utf-8

import sys
import os
from django.conf import settings

sys.path.append(settings.BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] ='mysite.settings'

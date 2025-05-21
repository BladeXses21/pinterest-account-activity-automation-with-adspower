import os
import sys

import django

sys.path.append("C:\\Users\\artur\\PycharmProjects\\Pinterest\\pinterestcom_project")
os.environ["DJANGO_SETTINGS_MODULE"] = "pinterestcom_project.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

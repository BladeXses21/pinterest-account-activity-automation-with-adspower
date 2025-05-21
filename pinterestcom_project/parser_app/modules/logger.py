from load_django import *
from parser_app.models import AccountLog

def log_account_action(profile, status, message=None, email=None):
    AccountLog.objects.create(
        email=email,
        profile=profile,
        status=status,
        message=message
    )

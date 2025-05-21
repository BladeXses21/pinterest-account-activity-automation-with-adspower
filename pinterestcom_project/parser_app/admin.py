from django.contrib import admin
from .models import Account, PinLink, AccountLog

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    list_display = ('email', 'password', 'profile_id', 'status')


@admin.register(AccountLog)
class AccountLog(admin.ModelAdmin):

    list_display = ('email', 'profile', 'status', 'message', 'timestamp')


@admin.register(PinLink)
class PinLinkAdmin(admin.ModelAdmin):

    list_display = ('url', 'status')

from django.db import models

class Account(models.Model):
    status = models.CharField(default='Active')

    email = models.EmailField()
    password = models.CharField(max_length=255)

    profile_id = models.CharField(max_length=75, blank=True)


    def __str__(self):
        return self.email


class AccountLog(models.Model):

    email = models.CharField(null=True)
    profile = models.CharField(max_length=50)
    status = models.CharField(max_length=100) # "Success", "Error", "Action", "Failed" ...
    message = models.TextField(blank=True, null=True) # "Liked pin http://...", or "Login failed"
    timestamp = models.DateTimeField(auto_now_add=True)


class PinLink(models.Model):
    status = models.CharField(default='Active')

    url = models.URLField()

    def __str__(self):
        return self.url



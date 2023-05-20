from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

from mastoapi.models import MastoApi

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api = models.ForeignKey(MastoApi, on_delete=models.CASCADE)
    media_uploads = models.BooleanField(default=True)
    note = models.CharField(max_length=140, blank=True, default="")

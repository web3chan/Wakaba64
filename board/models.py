from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

from mastoapi.models import MastoApi


class Status(models.Model):
    status_id = models.CharField(max_length=18)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"/res/{self.status_id}.html"

class MediaUpload(models.Model):
    media_id = models.CharField(max_length=18)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.media_id
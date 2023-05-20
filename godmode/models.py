from django.db import models

from django.contrib.auth.models import User

class Ban(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.DateTimeField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.user} expires at {self.expires}"

from django.contrib import admin

from .models import Status, MediaUpload

admin.site.register(Status)
admin.site.register(MediaUpload)
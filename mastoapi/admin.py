from django.contrib import admin

from .models import Instance, MastoApi

# Register your models here.
admin.site.register(Instance)
admin.site.register(MastoApi)
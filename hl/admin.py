from django.contrib import admin

# Register your models here.
from .models import YtChannel, YtVideo

admin.site.register(YtChannel)
admin.site.register(YtVideo)
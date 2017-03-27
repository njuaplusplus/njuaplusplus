from django.contrib import admin
from .models import ATimeLoggerProfile, ActivityType, Interval


admin.site.register(ATimeLoggerProfile)
admin.site.register(ActivityType)
admin.site.register(Interval)

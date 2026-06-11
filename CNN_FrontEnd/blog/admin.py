from django.contrib import admin
from .models import Post, AnomalyLog, SystemExceptionLog

# Register your models here.
admin.site.register(Post)
admin.site.register(AnomalyLog) # 이상징후 로그 DB
admin.site.register(SystemExceptionLog) # 시스템 오류 로그 DB

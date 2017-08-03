#coding:utf-8

from django.contrib import admin
from .models import *

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zh_name', 'desc', 'flag', 'creator', 'create_time', 'update_time')

admin.site.register(Role,RoleAdmin)

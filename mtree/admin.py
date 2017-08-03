#coding:utf-8
from django.contrib import admin
from mtree.models import *

class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'other_ip', 'hostname', 'port', 'idc', 'cpu', 'memory', 'disk', 'os', 'host_status', 'host_type', 'sn', 'create_time', 'is_active', 'comment')
    search_fields = ('id', 'ip', 'other_ip', 'hostname', 'port', 'idc', 'cpu', 'memory', 'disk', 'os', 'sn', 'comment')

class IdcAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zh_name', 'bandwidth', 'linkman', 'phone', 'address', 'network', 'create_time', 'operator', 'comment')

class MtreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'pid', 'deep', 'gen', 'zh_name', 'en_name', 'tags', 'create_time', 'update_time')
    search_fields = ('id', 'pid', 'deep', 'gen', 'zh_name', 'en_name', 'tags')

class Mtree_roleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zh_name', 'desc', 'create_time', 'update_time')
class Mtree_user_roleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'create_time', 'update_time')
    search_fields = ('user', 'role')
class Tmp_roleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'tree', 'day', 'create_time', 'update_time')
    search_fields = ('user', 'role', 'tree')
#class Mtree_hostAdmin(admin.ModelAdmin):
#    list_display = ('mtree', 'creator', 'create_time', 'update_time')


admin.site.register(Host,HostAdmin)
admin.site.register(Idc,IdcAdmin)

admin.site.register(Mtree,MtreeAdmin)
admin.site.register(Mtree_role,Mtree_roleAdmin)
admin.site.register(Mtree_user_role,Mtree_user_roleAdmin)
admin.site.register(Tmp_role,Tmp_roleAdmin)
#admin.site.register(Mtree_host,Mtree_hostAdmin)


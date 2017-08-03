#coding:utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


HOST_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"报废")
    )

HOST_TYPE = (
    (1, u"物理机"),
    (2, u"虚拟机"),
    (3, u"交换机"),
    (4, u"路由器"),
    (5, u"防火墙"),
    (6, u"Docker"),
    (7, u"其他")
    )

class Idc(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'机房名称')
    zh_name = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'机房中文名称')
    bandwidth = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'机房带宽')
    linkman = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name=u'联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'联系电话')
    address = models.CharField(max_length=128, blank=True, null=True, default='', verbose_name=u"机房地址")
    network = models.TextField(blank=True, null=True, default='', verbose_name=u"IP地址段")
    create_time = models.DateField(auto_now=True, null=True)
    operator = models.CharField(max_length=32, blank=True, default='', null=True, verbose_name=u"运营商")
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

class Mtree(models.Model):
    pid = models.IntegerField()
    deep = models.IntegerField()
    gen = models.CharField(max_length=20)
    zh_name = models.CharField(max_length=100)
    en_name = models.CharField(max_length=100)
    tags = models.CharField(max_length=1000, blank=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间',auto_now=True)
    def __str__(self):
        return str(self.id)

class Host(models.Model):
    ip = models.CharField(unique=True, max_length=32, null=True,verbose_name=u"主机IP")
    other_ip = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"其他IP")
    hostname = models.CharField(max_length=128, verbose_name=u"主机名")
    port = models.IntegerField(blank=True, default=22, verbose_name=u"端口号")
    idc = models.ForeignKey(Idc, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'机房')
    cpu = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name=u'CPU')
    memory = models.CharField(max_length=128, blank=True, null=True, default='', verbose_name=u'内存')
    disk = models.CharField(max_length=1024, blank=True, null=True, default='', verbose_name=u'硬盘')
    os = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u"操作系统")
    host_status = models.IntegerField(choices=HOST_STATUS, blank=True, default=1, verbose_name=u"机器状态")
    host_type = models.IntegerField(choices=HOST_TYPE, blank=True, null=True, verbose_name=u"主机类型")
    sn = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"SN编号")
    create_time = models.DateTimeField(auto_now=True, null=True)
    #is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    is_active = models.IntegerField(u'是否启用',default=1)
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")
    trees = models.ManyToManyField(Mtree,blank=True)

    def __unicode__(self):
        return self.ip


class Mtree_role(models.Model):
    name = models.CharField('角色名', max_length=50)
    zh_name = models.CharField('角色中文名', max_length=50) 
    desc = models.TextField(u'描述', blank=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间',auto_now=True)
    def __unicode__(self):
        return self.zh_name


class Mtree_user_role(models.Model):
    user = models.ForeignKey(User)
    role = models.ForeignKey(Mtree_role)
    trees = models.ManyToManyField(Mtree,blank=True)
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间',auto_now=True)
    class Meta:
        unique_together = (("user", "role"),)

class Tmp_role(models.Model):
    user = models.ForeignKey(User)
    role = models.ForeignKey(Mtree_role)
    tree = models.ForeignKey(Mtree)
    day = models.IntegerField(u'使用天数')
    create_time = models.DateTimeField(u'创建时间',auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间',auto_now=True)
    class Meta:
        unique_together = (("user", "role", "tree"),)

#!/usr/bin/env python2.7
#coding:utf-8
import ast
import time
import datetime
import os
import json
import re
import requests
from celery import task,platforms
from django.contrib.auth.models import User
from django.conf import settings
from mtree.models import *
from mtree.views import get_node_path_by_treeid
from mysite.comm import *
import logging
logger = logging.getLogger(__name__)

platforms.C_FORCE_ROOT = True

@task()
def sync_host(): 
    jump_host_api = 'https://jump.ops.hhr.com/japi/get_host_list/'
    ret,err = request_get(jump_host_api)
    result = False
    if not err: 
        rets = ret.json()
        ids = [row.id for row in Host.objects.all()]
        new_ids = [row['id'] for row in rets]
        delete_ids = [id for id in ids if id not in new_ids]
        Host.objects.filter(id__in=delete_ids).delete()
        for ret in rets:
            id = ret.pop('id')
            disk_info = ret.pop('disk')
            if disk_info:
                disk_dict = ast.literal_eval(disk_info)
                disk_list = sorted(disk_dict.values())
                ret['disk'] = ','.join(map(str, map(int,disk_list)))
            else:
                ret['disk'] = ''
            Host.objects.update_or_create(id=id,defaults=ret)
        result = True
    return result

@task()
def clear_role():
    rets = Tmp_role.objects.all()
    for ret in rets:
        if (datetime.date.today() - ret.create_time.date()).days > ret.day:
            r = Mtree_user_role.objects.get(role=ret.role,user=ret.user)
            r.trees.remove(ret.tree)
            Tmp_role.objects.filter(role=ret.role,user=ret.user,tree=ret.tree).delete()
    return 'done'

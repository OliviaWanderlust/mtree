#coding:utf-8
import json
import re
import datetime
from xpinyin import Pinyin
from collections import OrderedDict
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404 
from django.template.defaulttags import register
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from main.models import *
#from workflow.models import Work_order
from mysite.comm import *
from main.views import *
from .models import *

@register.filter
def get_node_path_by_treeid(id):
    if not id: return ''
    gen = Mtree.objects.get(id=int(id)).gen
    tree_id_list = gen.split('_')
    tree_id_list.remove('0')
    tree_id_list.remove(str(settings.INIT_TREE_ID))
    tree_name_list = [Mtree.objects.get(id=tree_id).zh_name for tree_id in tree_id_list]
    tree_names = '/' + '/'.join(tree_name_list)
    return tree_names

@register.filter
def get_cpu_num(cpu_info):
    if not cpu_info: return ''
    return cpu_info.split()[-1]

def require_mtree_role(username, treeid, role_list=None):
    ret = False
    try:
        tree_info = Mtree.objects.get(id=int(treeid))
    except:
        return ret
    gen = tree_info.gen
    treeids = [int(id) for id in gen.split('_')]
    if role_list:
        if Mtree_user_role.objects.filter(role__name__in=role_list, user__username=username, trees__id__in=treeids): ret = True
    else:
        if Mtree_user_role.objects.filter(user__username=username, trees__id__in=treeids): ret = True
    return ret

def getMtreePathById(id):
    try:
        gen = Mtree.objects.get(id=id).gen
        ids = gen.split('_')
        names = [row.zh_name for row in Mtree.objects.filter(id__in=ids)]
        ret = '/' + '/'.join(names)
    except:
        ret = ''
    return ret

def index(request):
    return HttpResponse('mtree index')

@login_required
def host_list(request):
    title = '主机列表'
    username = request.user.username
    treeid = request.session.get('treeid',settings.INIT_TREE_ID)
    modename = request.GET.get('modename',)
    key = request.GET.get('key','')
    mount_status = request.GET.get('mount_status','')
    ret = require_mtree_role(username, int(treeid))
    if not ret: return HttpResponse('您无该树节点访问权限<a href="/mtree/role_list?treeid=%s" target="_self">点击申请</a>' % treeid)
    tree_info = Mtree.objects.get(id=int(treeid))
    gen = tree_info.gen
    deep = tree_info.deep
    if deep <= 1: show_mount_status = 1
    if deep == 0:
        if key:
            rets = Host.objects.filter(Q(ip__contains=key)|Q(other_ip__contains=key)|Q(hostname__contains=key)|Q(os__contains=key)|Q(sn__contains=key)|Q(comment__contains=key)).distinct().order_by('hostname')
        else:
            if mount_status == '0':
               rets = Host.objects.filter(trees=None).distinct().order_by('hostname')
            elif mount_status == '1':
                rets = Host.objects.exclude(trees=None).distinct().order_by('hostname')
            else:
                rets = Host.objects.all().distinct().order_by('hostname')
    else:
        if key:
            rets = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees__id=treeid),Q(ip__contains=key)|Q(other_ip__contains=key)|Q(hostname__contains=key)|Q(os__contains=key)|Q(sn__contains=key)|Q(comment__contains=key)).distinct().order_by('hostname')
        else:
            if mount_status:
                tree_obj = Mtree.objects.get(gen__startswith=gen+'_', deep=settings.MAXDEEP, en_name='BackupPool')
                pool_host_list = Host.objects.filter(trees=tree_obj).distinct()
                mount_host_list = Host.objects.filter(Q(trees__gen__startswith=gen+'_'),~Q(trees=tree_obj)).distinct()
                if deep == 1 and mount_status == '0':
                    rets = [row for row in pool_host_list if row not in mount_host_list]
                elif deep == 1 and mount_status == '1':
                    rets = Host.objects.filter(Q(trees__gen__startswith=gen+'_'),~Q(trees=tree_obj)).distinct().order_by('hostname') 
            else:
                rets = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees__id=treeid)).distinct().order_by('hostname') 
    msgnum = len(rets)
    pagenum = settings.PAGE_LIMIT
    return render_to_response('mtree/host_list.html',locals())

@login_required
def search_host_mtree(request):
    key = request.GET.get('key','')
    title = '搜索主机挂载树节点'
    if key:
        rets = Host.objects.filter(Q(ip__contains=key)|Q(other_ip__contains=key)|Q(hostname__contains=key)).distinct().order_by('hostname')
    else:
        rets = Host.objects.order_by('hostname')
    msgnum = len(rets)
    pagenum = settings.PAGE_LIMIT
    return render_to_response('mtree/search_host_mtree.html',locals())

@login_required
def my_role_list(request):
    title = '我的权限列表'
    user = request.user
    rets =  Mtree_user_role.objects.filter(user=user,trees__id__gt=0).distinct()
    return render_to_response('mtree/my_role_list.html',locals())

@login_required
def host_mount(request):
    title = '主机挂载'
    username = request.user.username
    treeid = request.session.get('treeid',settings.INIT_TREE_ID)
    modename = request.GET.get('modename',)
    mount_node = request.GET.get('mount_node',)
    ret = require_mtree_role(username, int(treeid), role_list=['op', 'op_admin'])
    if not ret: return HttpResponse('您无该树节点访问权限<a href="/mtree/role_list?treeid=%s" target="_self">点击申请</a>' % treeid)
    tree_info = Mtree.objects.get(id=int(treeid))
    gen = tree_info.gen
    deep = tree_info.deep
    if deep == 0:
        mount_nodes = Mtree.objects.filter(deep=settings.MAXDEEP,en_name='BackupPool')
        all_host = Host.objects.exclude(trees__id__in=mount_nodes).distinct().order_by('hostname')
    elif deep == settings.MAXDEEP:
        mount_nodes = Mtree.objects.filter(id=int(treeid))
        gen = re.match('\d+_\d+_\d+',gen).group()
        all_host = Host.objects.filter(trees__gen__startswith=gen+'_').distinct().order_by('hostname')
    else:
        mount_nodes = Mtree.objects.filter(deep=settings.MAXDEEP,gen__startswith=gen+'_').exclude(deep=settings.MAXDEEP,en_name='BackupPool')
        gen = re.match('\d+_\d+_\d+',gen).group()
        all_host = Host.objects.filter(trees__gen__startswith=gen+'_').distinct().order_by('hostname')
    if mount_node:
        mount_node = int(mount_node)
        hosts = Host.objects.filter(trees__id=mount_node).distinct().order_by('hostname')
    else:
        if mount_nodes:
            hosts = Host.objects.filter(trees__id=mount_nodes[0].id).distinct().order_by('hostname')
        else:
            hosts = []
    return render_to_response('mtree/host_mount.html',locals())

@login_required
def ajax_mtree(request):
    ret = False
    username = request.user.username
    data = {}
    if request.method == 'POST':
        act = request.POST.get('act')
        mount_node = request.POST.get('mount_node')
        hosts = request.POST.get('hosts')
        if act == 'mount':
            if hosts:
                host_list = hosts.split(',')
            else: 
                host_list = []
            mtree_obj = Mtree.objects.get(id=int(mount_node))
            #判断是否有已经被挂载的主机被删除
            if mtree_obj.en_name == 'BackupPool':
                gen = re.match('\d+_\d+_\d+',mtree_obj.gen).group()
                mount_host_list = [row.id for row in Host.objects.filter(Q(trees__gen__startswith=gen+'_'),~Q(trees__id=int(mount_node))).distinct()]
                if list(set(mount_host_list).difference(set(map(int, host_list)))): return HttpResponse('不能删除已挂载的主机')
            if hosts:
                host_obj = Host.objects.filter(id__in=host_list)
                mtree_obj.host_set.clear()
                mtree_obj.host_set.add(*host_obj)
            else:
                mtree_obj.host_set.clear()
            ret = '操作成功'
                
        elif act == 'deluser':
            username = request.POST.get('username')
            treeid = request.POST.get('treeid')
            role_name = request.POST.get('role_name')
            mtree_obj = Mtree.objects.get(id=int(treeid))
            role_obj = Mtree_role.objects.get(name=role_name)
            user_obj = User.objects.get(username=username)
            ret = Mtree_user_role.objects.get(role__name=role_name,user__username=username)
            ret.trees.remove(mtree_obj)
            ret = '删除成功'
        elif act == 'adduser':
            username = request.POST.get('username')
            treeid = request.POST.get('treeid')
            role_name = request.POST.get('role_name')
            mtree_obj = Mtree.objects.get(id=int(treeid))
            role_obj = Mtree_role.objects.get(name=role_name)
            if not User.objects.filter(username=username): return HttpResponse('用户不存在')
            user_obj = User.objects.get(username=username)
            if not Mtree_user_role.objects.filter(role__name=role_name,user__username=username):
                ret = Mtree_user_role.objects.create(role=role_obj,user=user_obj)
            else:
                ret = Mtree_user_role.objects.get(role__name=role_name,user__username=username)
            ret.trees.add(mtree_obj)
            ret = 'ok'
        elif act == 'editnode':
            treeid = request.POST.get('treeid',)
            zh_name = request.POST.get('name',)
            ret = require_mtree_role(username, int(treeid), role_list=['op', 'op_admin'])
            if not ret: 
                data['error'] = '没权限'
                return HttpResponse(json.dumps(data))
            tree_info = Mtree.objects.get(id=int(treeid))
            gen = tree_info.gen
            deep = tree_info.deep
            p = Pinyin()
            en_name = p.get_pinyin(zh_name,'')
            Mtree.objects.filter(id=int(treeid)).update(zh_name=zh_name, en_name=en_name)
            return HttpResponse(json.dumps(data))
        elif act == 'addnode':
            zh_name = request.POST.get('name',)
            pid = request.POST.get('pid',)
            ret = require_mtree_role(username, int(pid), role_list=['op', 'op_admin'])
            if not ret:
                data['error'] = '没权限'
                return HttpResponse(json.dumps(data))
            p = Pinyin()
            en_name = p.get_pinyin(zh_name, '')
            if int(pid) == 0:
                pgen = str(0)
                pdeep = 0
            else:
                pnode = Mtree.objects.get(id=pid)
                pgen = pnode.gen
                pdeep = pnode.deep
            deep = pdeep + 1
            if deep == settings.MAXDEEP and en_name == 'BackupPool':
                data['error'] = '不能创建名为BackupPool的主机挂载节点'
                return HttpResponse(json.dumps(data))
            ret = Mtree.objects.create(pid=pid, deep=deep, zh_name=zh_name, en_name=en_name)
            id = ret.id
            gen = pgen + '_' + str(id)
            Mtree.objects.filter(id=id).update(gen=gen)
            #创建一级节点自动添加备机池
            if deep == 1:
                en_name = zh_name = 'BackupPool'
                for i in range(2,5):
                    deep = i
                    pid = id
                    ret = Mtree.objects.create(pid=pid, deep=deep, zh_name=zh_name, en_name=en_name)
                    id = ret.id
                    gen = gen + '_' + str(id)
                    Mtree.objects.filter(id=id).update(gen=gen)
                data['error'] = '自动增加备机池，刷新页面'
                return HttpResponse(json.dumps(data))
            showid = 2
            if deep == settings.MAXDEEP: showid = 1
            data = {'id':id,'showid':showid,'deep':deep}
            return HttpResponse(json.dumps(data))
        elif act == 'delnode':
            treeid = request.POST.get('treeid',)
            ret = require_mtree_role(username, int(treeid), role_list=['op', 'op_admin'])
            if not ret: 
                data['error'] = '没权限'
                return HttpResponse(json.dumps(data))
            tree_info = Mtree.objects.get(id=int(treeid))
            gen = tree_info.gen
            deep = tree_info.deep
            hosts = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees__id=int(treeid)))
            if hosts:
                data['error'] = '节点有挂载机器，不能删除'
                return HttpResponse(json.dumps(data))
            if deep < settings.MAXDEEP:
                rets = Mtree.objects.filter(Q(gen__contains='_%s_' % treeid)|Q(id=treeid))
                treeids = [row.id for row in rets]
                Mtree.objects.filter(Q(gen__contains='_%s_' % treeid)|Q(id=treeid)).delete()
            else:
                Mtree.objects.filter(id=treeid).delete()
            return HttpResponse(json.dumps(data))
        elif act == 'dropnode':
            treeid = request.POST.get('treeid',)
            dtreeid = request.POST.get('dtreeid',)
            tree_obj = Mtree.objects.get(id=int(treeid))
            deep = tree_obj.deep
            gen = tree_obj.gen
            hosts = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees__id=int(treeid))).distinct()
            if hosts:
                if deep != Mtree.objects.get(id=int(dtreeid)).deep + 1:
                    data['error'] = '目标数节点有挂载主机，只支持同层级拖拽'
                    return HttpResponse(json.dumps(data))
            if deep < Mtree.objects.get(id=int(dtreeid)).deep + 1:
                data['error'] = '只支持同层级或高层级向低层级拖拽'
                return HttpResponse(json.dumps(data))
            if not 'mtree_admin' in get_roles_by_username(username): 
                data['error'] = '没权限'
                return HttpResponse(json.dumps(data))
            if not Mtree.objects.filter(id=int(treeid)).update(pid=int(dtreeid)):
                data['error'] = '节点拖拽失败'
            return HttpResponse(json.dumps(data))
        elif act == 'add_host':
            idc_id = request.POST.get('idc_id')
            hostname = request.POST.get('hostname').strip()
            ip = request.POST.get('ip').strip()
            other_ip = request.POST.get('other_ip').strip()
            os = request.POST.get('os').strip()
            cpu = request.POST.get('cpu').strip()
            memory = request.POST.get('memory').strip()
            disk = request.POST.get('disk').strip()
            is_active = request.POST.get('is_active')
            port = request.POST.get('port').strip()
            comment = request.POST.get('comment').strip()
            idc_obj = Idc.objects.get(id=int(idc_id))
            if Host.objects.filter(ip=ip):
                ret = '添加失败，内网IP已经存在'
            else:
                ret = Host.objects.create(hostname=hostname, ip=ip, other_ip=other_ip, port=int(port), os=os, cpu=cpu, memory=memory, disk=disk, is_active=int(is_active), idc=idc_obj, comment=comment)
                if ret: ret = '添加成功'
        elif act == 'del_host':
            id = request.POST.get('id')
            ret = Host.objects.filter(id=int(id)).delete()
            if ret: ret = '删除成功'
        elif act == 'edit_host':
            id = request.POST.get('id')
            idc_id = request.POST.get('idc_id')
            hostname = request.POST.get('hostname')
            ip = request.POST.get('ip')
            other_ip = request.POST.get('other_ip')
            is_active = request.POST.get('is_active')
            port = request.POST.get('port').strip()
            os = request.POST.get('os').strip()
            cpu = request.POST.get('cpu').strip()
            memory = request.POST.get('memory').strip()
            disk = request.POST.get('disk').strip()
            comment = request.POST.get('comment').strip()
            idc_obj = Idc.objects.get(id=int(idc_id))
            if Host.objects.filter(id=int(id)):
                ret = Host.objects.filter(id=int(id)).update(hostname=hostname, ip=ip, other_ip=other_ip, port=int(port), os=os, cpu=cpu, memory=memory, disk=disk, is_active=int(is_active), idc=idc_obj, comment=comment)
                if ret: ret = '修改成功'
            else:
                ret = 'id不存在'
        elif act == 'add_idc':
            name = request.POST.get('name').strip()
            zh_name = request.POST.get('zh_name').strip()
            bandwidth = request.POST.get('bandwidth').strip()
            linkman = request.POST.get('linkman').strip()
            phone = request.POST.get('phone').strip()
            address = request.POST.get('address').strip()
            network = request.POST.get('network').strip()
            operator = request.POST.get('operator').strip()
            comment = request.POST.get('comment').strip()
            if Idc.objects.filter(name=name):
                ret = '添加失败，机房名已经存在'
            else:
                ret = Idc.objects.create(name=name, zh_name=zh_name, bandwidth=bandwidth, linkman=linkman, phone=phone, address=address, network=network, operator=operator, comment=comment)
                if ret: ret = '添加成功'
        elif act == 'del_idc':
            id = request.POST.get('id')
            ret = Idc.objects.filter(id=int(id)).delete()
            if ret: ret = '删除成功'
        elif act == 'edit_idc':
            id = request.POST.get('id')
            name = request.POST.get('name').strip()
            zh_name = request.POST.get('zh_name').strip()
            bandwidth = request.POST.get('bandwidth').strip()
            linkman = request.POST.get('linkman').strip()
            phone = request.POST.get('phone').strip()
            address = request.POST.get('address').strip()
            network = request.POST.get('network').strip()
            operator = request.POST.get('operator').strip()
            comment = request.POST.get('comment').strip()
            if Idc.objects.filter(id=int(id)):
                ret = Idc.objects.filter(id=int(id)).update(name=name, zh_name=zh_name, bandwidth=bandwidth, linkman=linkman, phone=phone, address=address, network=network, operator=operator, comment=comment)
                if ret: ret = '修改成功'
            else:
                ret = 'id不存在'
    return HttpResponse(ret)

#@login_required
def get_hosts_by_treeid(request):
    treeid = request.GET.get('treeid',)
    tree_info = Mtree.objects.get(id=int(treeid))
    gen = tree_info.gen
    hosts = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees__id=int(treeid))).distinct().order_by('hostname') 
    data = []
    for host in hosts:
        data.append([host.hostname,host.ip])
    return HttpResponse(json.dumps(data,separators=(',',':')))

def get_hosts_by_username(request):
    username = request.GET.get('username',)
    treeid = request.GET.get('treeid',)
    if not username: return HttpResponse(json.dumps([]))
    if treeid:
        role_list = []
        tree_obj = Mtree.objects.get(id=int(treeid))
        gen = tree_obj.gen
        rets = Mtree_user_role.objects.filter(user__username=username, trees__gt=0).distinct()
        op_tree_list = []
        rd_tree_list = []
        for ret in rets:
            if ret.role.name in ['op', 'op_admin']:
                op_tree_list.extend(ret.trees.all())
            else:
                rd_tree_list.extend(ret.trees.all())
        if [row for row in op_tree_list if gen in row.gen]: role_list.append('bbtree_OP')
        if [row for row in rd_tree_list if gen in row.gen]: role_list.append('bbtree_RD')
        all_host_list = Host.objects.filter(Q(trees__gen__startswith=gen+'_')|Q(trees=tree_obj)).distinct()
        data = []
        for host in all_host_list:
            ret = {}
            ret['ip'] = host.ip
            ret['hostname'] = host.hostname
            ret['other_ip'] = host.other_ip
            ret['port'] = host.port
            ret['sysuser'] = ','.join(role_list)
            data.append(ret)
        return HttpResponse(json.dumps(data))
    rets = Mtree_user_role.objects.filter(user__username=username,trees__id__gt=0).distinct()
    op_tree_list = []
    op_host_list = []
    rd_tree_list = []
    rd_host_list = []
    for ret in rets:
        if ret.role.name in ['op', 'op_admin']:
            op_tree_list.extend(ret.trees.all())
        else:
            rd_tree_list.extend(ret.trees.all())
    op_tree_list = list(set(op_tree_list))
    rd_tree_list = list(set(rd_tree_list))
    for tree in op_tree_list:
        op_host_list.extend(Host.objects.filter(Q(trees__gen__startswith=tree.gen+'_')|Q(trees=tree)).distinct())
    op_host_list = list(set(op_host_list))
    for tree in rd_tree_list:
        rd_host_list.extend(Host.objects.filter(Q(trees__gen__startswith=tree.gen+'_')|Q(trees=tree)).distinct())
    rd_host_list = list(set(rd_host_list))
    both_host_list = list(set(rd_host_list) & set(op_host_list))
    all_host_list = list(set(rd_host_list) | set(op_host_list)) 
    data = []
    for host in all_host_list:
        ret = {}
        ret['ip'] = host.ip
        ret['hostname'] = host.hostname
        ret['other_ip'] = host.other_ip
        ret['port'] = host.port
        if host in both_host_list:
            ret['sysuser'] = 'bbtree_OP,bbtree_RD'
        elif host in op_host_list:
            ret['sysuser'] = 'bbtree_OP'
        else:
            ret['sysuser'] = 'bbtree_RD'
        data.append(ret)
    return HttpResponse(json.dumps(data))

def get_trees_by_username(request):
    username = request.GET.get('username',)
    if not username: return HttpResponse(json.dumps([]))
    rets = Mtree_user_role.objects.filter(user__username=username,trees__id__gt=0).distinct()
    tree_list = []
    for ret in rets:
        tree_list.extend(ret.trees.all())
    tree_list = list(set(tree_list))
    data = []
    for tree in tree_list:
        ret = {}
        ret['id'] = tree.id
        ret['path'] = get_node_path_by_treeid(tree.id)
        data.append(ret)
    return HttpResponse(json.dumps(data))

@login_required
def mtree(request):
    username = request.user.username
    if 'mtree_admin' in get_roles_by_username(username): is_mtree_admin = 1
    data = Mtree.objects.all()
    rootids = [0]
    zNodes = "["
    for i in data:
        id = i.id
        pid = i.pid
        deepnum = i.deep
        name = i.zh_name
        gen = i.gen.split('_')
        gen = [int(i) for i in gen]
        showid = 0
        newlist = list(set(rootids).intersection(set(gen)))
        if newlist:
            showid = 2
            if deepnum == settings.MAXDEEP: showid = 1
        zNodes += "{id:%s,pId:%s,name:'%s',showid:%s, iconSkin:'icon0%d'}," %(id, pid, name, showid, deepnum)
    zNodes += "]"
    #if "treeid" in request.session:
    #    treeid = request.session["treeid"]
    #else:
    #    request.session['treeid'] = treeid = settings.INIT_TREE_ID
    treeid = request.session.get('treeid',settings.INIT_TREE_ID)
    return render_to_response('mtree/mtree.html',locals())

def getMtreePath(request):
    id = request.GET.get('id',)
    nodepath = getMtreePathById(int(id))
    return HttpResponse(nodepath)

def getMtree(request):
    id = request.GET.get('id',)
    if not id: return HttpResponse("error: id不能为空")
    rets = Mtree.objects.filter(Q(gen__contains='_%s_' % id)|Q(id=int(id)))
    data = []
    for ret in rets:
        id = ret.id
        nodepath = getMtreePathById(id)
        data.append(nodepath)
    return HttpResponse(json.dumps(data))

@login_required
def get_mtree_admin(request):
    username = request.user.username
    treeid = request.GET.get('treeid',)
    role = request.GET.get('role',)
    tree_info = Mtree.objects.get(id=int(treeid))
    gen = tree_info.gen
    treeids = [int(id) for id in gen.split('_')]
    if not '_admin' in role: role = role + '_admin'
    rets = [{'username':row.user.username,'email':row.user.email, 'last_name':row.user.last_name} for row in Mtree_user_role.objects.filter(role__name=role,trees__id__in=treeids).distinct()]
    #if not rets:
    #    order_info = Work_order.objects.get(name='mtree_role')
    #    order_flow = order_info.flow
    #    role_id = order_flow.split('-')[0]        
    #    rets = [{'username':row.username,'email':row.email, 'last_name':row.last_name} for row in Role.objects.get(id=role_id).users.all()]
    return HttpResponse(json.dumps(rets))

@login_required
def role_list(request):
    title = '节点角色权限列表'
    username = request.user.username
    treeid = request.session.get('treeid',settings.INIT_TREE_ID)
    try:
        tree_info = Mtree.objects.get(id=treeid)
    except:
        return HttpResponse('树节点不存在')
    gen = tree_info.gen
    treeids = [int(id) for id in gen.split('_')]
    roles = Mtree_role.objects.order_by('name')
    #order_id = Work_order.objects.get(name='mtree_role').id
    rets = []
    for role in roles:
        ret = {}
        ret['name'] = role_admin_name = role_name = role.name
        ret['zh_name'] = role.zh_name
        ret['desc'] = role.desc
        ret['is_admin'] = ret['flag'] = 0
        if not '_admin' in role_name: role_admin_name = role_name + '_admin'
        if Mtree_user_role.objects.filter(user__username=username, role__name=role.name,trees__id__in=treeids).distinct(): ret['flag'] = 1
        if Mtree_user_role.objects.filter(user__username=username, role__name=role_admin_name, trees__id__in=treeids).distinct(): ret['is_admin'] = 1
        roles = get_roles_by_username(username)
        if 'mtree_admin' in roles: ret['is_admin'] =1
        #ret['users'] = [row.username for row in Mtree_user_role.objects.filter(role__zh_name=role.zh_name,trees__id__in=treeids).distinct()]
        ret['cur_users'] = cur_users = [ (row.user.username,row.user.email,row.user.last_name) for row in Mtree_user_role.objects.filter(role__name=role_name,trees__id=int(treeid)).distinct()]
        all_users = [ (row.user.username,row.user.email,row.user.last_name) for row in Mtree_user_role.objects.filter(role__name=role_name,trees__id__in=treeids).distinct()]
        ret['users'] = list(set(all_users).difference(set(cur_users)))
        rets.append(ret)
    return render_to_response('mtree/role_list.html',locals())

@require_role(role_list=['mtree_admin'])
def refresh_mtree(request):
    #刷新基因链，当拖拽节点或者手动修改数据都有可能导致基因链错误，发现基因链不对需要由业务树管理员访问下该接口自动修复基因链
    rets = Mtree.objects.all()
    #nodes = {1:0,2:0,3:1,4:5,5:3}
    nodes = {}
    for i in rets:
        nodes[i.id] = i.pid
    ids = nodes.keys()
    while ids:
        node_list = []
        id = nid = ids.pop()
        while id:
            node_list.append(id)
            pid = nodes[id]
            if pid == 0: node_list.append(pid)
            id = pid
        gen = '_'.join(map(str, reversed(node_list)))
        deep = len(node_list) -2
        Mtree.objects.filter(id=nid).update(gen=gen,deep=deep)
    #自动创建备机池节点
    for ret in rets:
        if ret.deep == 1:
            id = ret.id
            gen = ret.gen
            if Mtree.objects.filter(deep=settings.MAXDEEP,gen__startswith=gen+'_',en_name='BackupPool'): continue
            en_name = zh_name = 'BackupPool'
            for i in range(2,5):
                deep = i
                pid = id
                ret = Mtree.objects.create(pid=pid, deep=deep, zh_name=zh_name, en_name=en_name)
                id = ret.id
                gen = gen + '_' + str(id)
                Mtree.objects.filter(id=id).update(gen=gen)
    #大部门之间拖拽需要把备机池挂载节点的机器列表
    rets = Mtree.objects.filter(deep=1)
    for ret in rets:
        id = ret.id
        gen = ret.gen
        pool_tree = Mtree.objects.get(deep=settings.MAXDEEP,gen__startswith=gen+'_',en_name='BackupPool')
        pool_host_list = Host.objects.filter(trees=pool_tree).distinct()
        all_host_list = Host.objects.filter(trees__gen__startswith=gen+'_').distinct()
        if len(all_host_list) > len(pool_host_list):
            new_host_list = [host for host in all_host_list if host not in pool_host_list]
            pool_tree.host_set.add(*new_host_list)
            for host in new_host_list:
                trees_obj = host.trees.exclude(gen__startswith=gen+'_')
                host.trees.remove(*trees_obj)
    return HttpResponse('done')

def get_mtree(request):
    rets = Mtree.objects.all()
    data = []
    for ret in rets:
        r = {}
        r['id'] = ret.id
        r['pid'] = ret.pid
        r['gen'] = ret.gen
        r['deep'] = ret.deep
        r['en_name'] = ret.en_name
        r['zh_name'] = ret.zh_name
        data.append(r)
    return HttpResponse(json.dumps(data))

def get_mtree_sub(request):
    treeid = request.GET.get('treeid',)
    tree_obj = Mtree.objects.get(id=int(treeid))
    gen = tree_obj.gen
    deep = tree_obj.deep
    rets = Mtree.objects.filter(deep=deep+1,gen__startswith=gen+'_')
    data = []
    for ret in rets:
        r = OrderedDict()
        r['id'] = ret.id
        r['pid'] = ret.pid
        r['gen'] = ret.gen
        r['deep'] = ret.deep
        r['en_name'] = ret.en_name
        r['zh_name'] = ret.zh_name
        data.append(r)
    return HttpResponse(json.dumps(data,separators=(',',':')))

@login_required
def host_manage(request):
    title = '主机管理'
    username = request.user.username
    key = request.GET.get('key','')
    if key:
        rets = Host.objects.filter(Q(ip__contains=key)|Q(other_ip__contains=key)|Q(hostname__contains=key)|Q(os__contains=key)|Q(sn__contains=key)|Q(comment__contains=key)).distinct().order_by('hostname')
    else:
        rets = Host.objects.order_by('hostname')
    msgnum = len(rets)
    pagenum = settings.PAGE_LIMIT
    return render_to_response('mtree/host_manage.html',locals())

@login_required
def add_host(request):
    title = '添加主机'
    act = 'add_host'
    username = request.user.username
    idc_list = Idc.objects.order_by('-zh_name')
    return render_to_response('mtree/add_host.html',locals())

@login_required
def edit_host(request):
    title = '修改主机'
    act = 'edit_host'
    id = request.GET.get('id')
    if id:
        ret = Host.objects.get(id=int(id))
    else:
        return HttpResponse('参数错误')
    idc_list = Idc.objects.order_by('-zh_name')
    return render_to_response('mtree/edit_host.html',locals())

@login_required
def idc_list(request):
    title = 'IDC机房列表'
    username = request.user.username
    key = request.GET.get('key','')
    if key:
        rets = Idc.objects.filter(Q(name__contains=key)|Q(zh_name__contains=key)|Q(linkman__contains=key)|Q(phone__contains=key)|Q(address__contains=key)|Q(comment__contains=key)).distinct().order_by('name')
    else:
        rets = Idc.objects.order_by('name')
    msgnum = len(rets)
    pagenum = settings.PAGE_LIMIT
    return render_to_response('mtree/idc_list.html',locals())

@login_required
def add_idc(request):
    title = '添加机房'
    act = 'add_idc'
    username = request.user.username
    return render_to_response('mtree/add_idc.html',locals())

@login_required
def edit_idc(request):
    title = '修改机房信息'
    act = 'edit_idc'
    id = request.GET.get('id')
    if id:
        ret = Idc.objects.get(id=int(id))
    else:
        return HttpResponse('参数错误')
    return render_to_response('mtree/edit_idc.html',locals())

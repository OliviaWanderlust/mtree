#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from mtree.views import *

urlpatterns = [
    url(r'^index$', index),
    url(r'^mtree$', mtree),
    url(r'^getMtreePath$', getMtreePath),
    url(r'^getMtree$', getMtree),
    url(r'^get_mtree_admin$', get_mtree_admin),
    url(r'^host_list$', host_list),
    url(r'^my_role_list$', my_role_list),
    url(r'^host_mount$', host_mount),
    url(r'^ajax_mtree$', ajax_mtree),
    url(r'^role_list$', role_list),
    url(r'^get_hosts_by_treeid$', get_hosts_by_treeid),
    url(r'^get_hosts_by_username$', get_hosts_by_username),
    url(r'^get_trees_by_username$', get_trees_by_username),
    url(r'^refresh_mtree', refresh_mtree),
    url(r'^get_mtree$', get_mtree),
    url(r'^get_mtree_sub$', get_mtree_sub),
    url(r'^search_host_mtree$', search_host_mtree),
    url(r'^host_manage$', host_manage),
    url(r'^add_host$', add_host),
    url(r'^edit_host$', edit_host),
    url(r'^idc_list$', idc_list),
    url(r'^add_idc$', add_idc),
    url(r'^edit_idc$', edit_idc),
]

#coding:utf-8
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, include, url
from main.views import *

urlpatterns = [
    url(r'^$', index),
    url(r'^updatemain$', updatemain),
    url(r'^health$', health,name='health'),
    url(r'^login/$', login),
    url(r'^logout$', logout),
    url(r'^accounts/login/$', login),
    url(r'^add_role$', add_role),
    url(r'^edit_role$', edit_role),
    url(r'^role_list$', role_list),
    url(r'^ajax_role$', ajax_role),
    url(r'^get_role_users$', get_role_users),
    url(r'^get_user_roles$', get_user_roles),
]

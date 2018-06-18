# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from pushtoken import views

urlpatterns = [
    url(r'^send_push/$', views.send_push, name='send_push'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^$', views.set_settings, name='set_settings'),
]

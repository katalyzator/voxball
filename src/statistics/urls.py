# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from statistics import views

urlpatterns = [
    url(r'^search/$', views.search, name='search'),
]

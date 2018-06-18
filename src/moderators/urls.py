# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from moderators import views

urlpatterns = [
    url(r'^articles/related/$', views.get_polls_related_to_article, name='polls_by_article'),
    url(r'^articles/get/$', views.get_articles, name='get_articles'),
    url(r'^articles/delete/$', views.delete_article, name='delete_article'),
    url(r'^articles/add/$', views.add_article, name='add_article'),
    url(r'^articles/update/$', views.update_article, name='update_article'),
    url(r'^articles/statistics/$', views.get_articles_stat, name='get_articles_stat'),

    url(r'^category/create/$', views.category_create, name='category_create'),
    url(r'^category/read/$', views.category_read, name='category_read'),
    url(r'^category/update/$', views.category_update, name='category_update'),
    url(r'^category/delete/$', views.category_delete, name='category_delete'),

    url(r'^polls/feed/$', views.poll_feed, name='feed'),
    url(r'^polls/read/$', views.poll_read, name='read'),
    url(r'^polls/delete/$', views.poll_delete, name='delete'),
    url(r'^polls/get_polls_by_title/$', views.get_polls_by_title, name='get_polls_by_title'),
    url(r'^polls/approve/$', views.poll_approve, name='poll_approve'),

    url(r'^template/create/$', views.create, name='create'),
    url(r'^template/read/$', views.read, name='read'),
    url(r'^template/update/$', views.update, name='update'),
    url(r'^template/delete/$', views.delete, name='delete'),
    url(r'^template/feed/$', views.feed, name='feed'),
    url(r'^get_polls/$', views.get_polls, name='get_polls'),
    url(r'^get_users/$', views.get_users, name='get_users'),
]

# -*- coding: utf-8 -*-
from django.conf.urls import url
from polls import views

urlpatterns = [
    url(r'^get_user_info_and_polls/$', views.get_user_info_and_polls, name='get_user_info_and_polls'),
    url(r'^get_polls_votes_count/$', views.get_polls_votes_count, name='get_polls_votes_count'),
    url(r'^create_comment/$', views.create_comment, name='create_comment'),
    url(r'^get_comments/$', views.get_comment, name='get_comments'),
    url(r'^delete_comment/$', views.delete_comment, name='delete_comment'),
    url(r'^create/$', views.create, name='create'),
    url(r'^read/$', views.read, name='read'),
    url(r'^read/v2/$', views.read_v2, name='read_v2'),
    url(r'^update/$', views.update, name='update'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^answer_to_poll/$', views.answer_to_poll, name='answer_to_poll'),
    url(r'^view_poll/$', views.view_poll, name='view_poll'),
    url(r'^get_all_categories/$', views.get_all_categories, name='get_all_categories'),
    url(r'^get_all_poll_templates/$', views.get_all_poll_templates, name='get_all_poll_templates'),
    url(r'^get_all_keywords/$', views.get_all_keywords, name='get_all_keywords'),
    url(r'^get_random_poll/$', views.get_random_poll, name='get_random_poll'),
    url(r'^widget/get/$', views.get_widget_poll, name='get_widget_poll'),
    url(r'^article/get/$', views.get_article_poll, name='get_article_poll'),
    url(r'^repost/$', views.repost, name='repost'),
    url(r'^(?P<poll_id>\d+)/$', views.shared_poll_v3, name='shared_poll_v3'),
    url(r'^(?P<private_code>\w+)/$', views.shared_poll, name='shared_poll'),
    url(r'^front/poll/shared/(?P<user_id>\w+)/(?P<timestamp>\d+)/$', views.shared_poll_v2, name='shared_poll_v2'),
]

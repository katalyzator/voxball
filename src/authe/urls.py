# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from views import *

urlpatterns = [
    url(r'^amazon/bounces/$', handle_bounces, name='handle_bounces'),
    url(r'^amazon/complaints/$', handle_complaints, name='handle_complaints'),
    url(r'^app/version/$', app_version, name='app_version'),

    url(r'^register/$', register, name='register'),
    url(r'^sms_register/$', sms_register, name='sms_register'),
    url(r'^sms_activate/$', sms_user_activate, name='sms_activate'),
    url(r'^account_activate/(?P<key>\w+)/$', account_activate, name='account_activate'),

    url(r'^activate_account_by_token/$', activate_account_by_token, name='activate_account_by_token'),
    
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^facebook_login/$', facebook_login, name='facebook_login'),
    url(r'^reset/$', reset_password),
    url(r'^reset_password/$', set_password_by_code, name='set_password_by_code'),
    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^update_profile/$', update_profile, name='update_profile'),
    url(r'^get_user/$', get_user, name='get_user'),
    url(r'^get_users/$', get_users, name='get_users'),
    url(r'^sms_redirect/$', sms_redirect, name='sms_redirect'),
    url(r'^sms_resend/$', sms_resend, name='sms_resend'),
    url(r'^login/check/$', check_login, name='check_login'),

    url(r'^countries/$', countries, name='countries'),
    url(r'^cities/(?P<country_id>\d+)/$', cities, name='cities'),

    url(r'^profile/activate_new_email/(?P<key>\w+)/$', activate_new_email, name='activate_new_email'),
    url(r'^profile/activate_new_phone/$', activate_new_phone, name='activate_new_phone'),
    url(r'^profile/categories/$', update_user_categories, name='update_user_categories'),
    url(r'^profile/category/add_delete/$', add_delete_category, name='add_delete_category'),

    url(r'^csrf/$', get_csrf, name='get_csrf'),
    url(r'^csrf/verify/$', verify_csrf, name='verify_csrf'),
]

# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import redirect


def handler500(request):
    return redirect(settings.FRONT_404)


def handler404(request):
    return redirect(settings.FRONT_404)


def handler400(request):
    return redirect(settings.FRONT_404)

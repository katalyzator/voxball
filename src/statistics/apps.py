# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class StatisticsConfig(AppConfig):
    name = 'statistics'

    def ready(self):
        import statistics.signals

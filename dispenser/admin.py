# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from models import Device, Chamber, DispenseLog
from doctor.models import Schedule

admin.site.register(Device)
admin.site.register(Chamber)
admin.site.register(Schedule)
admin.site.register(DispenseLog)

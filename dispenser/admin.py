# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from doctor.models import Item
# Register your models here.
from models import Device, Chamber, DispenseLog, Load, LoadData

admin.site.register(Device)
admin.site.register(Chamber)
admin.site.register(Item)
admin.site.register(DispenseLog)
admin.site.register(Load)
admin.site.register(LoadData)

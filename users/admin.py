# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from users.models import Consumption, User

admin.site.register(Consumption)
admin.site.register(User)

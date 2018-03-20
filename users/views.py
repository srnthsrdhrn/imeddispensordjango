# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from users.models import User


def landing_page(request):
    return render(request, 'theme/index.html')


def login_success(request):
    if request.user.account_type == User.DOCTOR:
        return redirect('doctor_dashboard')
    return render(request, 'admin_theme/dashboard.html')

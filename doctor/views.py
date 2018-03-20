# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import render

# Create your views here.
from doctor.forms import DiagnosisForm


def dashboard(request):
    user = request.user
    patients_count = user.patient_prescriptions.values('patient').distinct().count()
    return render(request, 'doctor/doctor_panel.html', {'patients_count': patients_count})


def new_diagnosis(request):
    form = DiagnosisForm()
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            messages.success(request, "Stored Success")
    return render(request, 'doctor/new_diagnosis.html',{'form':form})

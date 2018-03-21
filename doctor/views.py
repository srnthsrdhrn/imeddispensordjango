# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import render

# Create your views here.
from doctor.forms import DiagnosisForm
from users.models import User


def dashboard(request):
    user = request.user
    patients_count = user.patient_prescriptions.values('patient').distinct().count()
    return render(request, 'doctor/doctor_panel.html', {'patients_count': patients_count})


def check_patient(request):
    user = None
    if request.method == 'POST':
        data = request.POST.get("aadhar_number")
        try:
            user = User.objects.get(aadhar_number=data)
        except User.DoesNotExist, e:
            messages.add_message(request, messages.WARNING, "User with that Aadhar Number does not exist")
        except ValueError, e:
            messages.add_message(request, messages.WARNING, "User with that Aadhar Number does not exist")
    return render(request, 'doctor/check_patient.html', {'user': user})


def new_diagnosis(request, patient_id):
    form = DiagnosisForm()
    return render(request, 'doctor/new_diagnosis.html', {'form': form, 'patient_id': patient_id})

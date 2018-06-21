# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.views import APIView

from doctor.forms import DiagnosisForm, PharmacistDiagnosisForm
from doctor.models import Prescription
from users.models import User


# Create your views here.


@login_required
def dashboard(request):
    user = request.user
    patients_count = user.doctor_prescriptions.values('patient').distinct().count()
    return render(request, 'doctor/doctor_panel.html', {'patients_count': patients_count})


@login_required
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


@login_required
def new_diagnosis(request, patient_id):
    form = DiagnosisForm()
    return render(request, 'doctor/new_diagnosis.html', {'form': form, 'patient_id': patient_id})


@login_required
def patient_list(request):
    patients = request.user.doctor_prescriptions.values('patient').distinct()
    patient_user = []
    for id in patients:
        patient_user.append(User.objects.get(id=id['patient']))
    return render(request, 'doctor/patient_list.html', {'patients': patient_user})


def patient_prescription_view(request, patient_id):
    patient = User.objects.get(id=patient_id)
    prescriptions = patient.patient_prescriptions.all()
    return render(request, 'doctor/patient_prescription_list.html',
                  {'name': patient.first_name, 'prescriptions': prescriptions})


def prescription_view(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    return render(request, 'doctor/prescription_view.html', {'prescription': prescription})


def pharmacist_prescription_upload(request):
    form = PharmacistDiagnosisForm()
    return render(request, 'doctor/new_pharmacist_prescription.html', {'form': form})


def complete_pharmacist_prescription(request):
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        pass
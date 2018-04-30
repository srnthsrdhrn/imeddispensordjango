# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.db.models import Sum

from doctor.models import CustomManager, Schedule, Prescription, Composition


class User(AbstractUser):
    ADMIN = 0
    DOCTOR = 1
    PATIENT = 2
    VENDOR = 3
    ACCOUNT_TYPES = ((ADMIN, "Admin"), (DOCTOR, "Doctor"), (PATIENT, "Patient"), (VENDOR, "Vendor"))
    mobile_number = models.BigIntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    aadhar_number = models.BigIntegerField(null=True, blank=True, unique=True)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=PATIENT)
    profile_pic = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def get_patient_prescription(self):
        schedules = []
        for slot in Schedule.SLOT_CHOICES:
            compositions = Schedule.objects.filter(prescription__patient=self, slot=slot[0]).values(
                'composition').distinct()
            data = []
            for composition in compositions:
                composition = Composition.objects.get(id=composition['composition'])
                schedule = Schedule.objects.filter(prescription__patient=self, slot=slot[0],
                                                   composition=composition)
                total = schedule.aggregate(Sum("qty"))['qty__sum']
                data.append({'composition': composition.name, 'quantity': total})
            schedules.append({'data': data, 'slot': slot})
        return schedules

    def get_patient_prescription_dispense(self):
        data = []
        compositions = Schedule.objects.filter(prescription__patient=self).values(
            'composition').distinct()
        for composition in compositions:
            composition = Composition.objects.get(id=composition['composition'])
            schedules = Schedule.objects.filter(prescription__patient=self,
                                                composition=composition)
            total = 0
            for schedule in schedules:
                total += schedule.qty * schedule.no_of_days
            data.append({'composition': composition.name, 'quantity': total})
        return data


class ConsumptionLog(models.Model):
    patient = models.ForeignKey(User, limit_choices_to={'account_type': User.PATIENT})
    schedule = models.ForeignKey('doctor.Schedule', related_name='consumptions')
    consumed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.db.models import Sum

from doctor.models import CustomManager, Item, Prescription, Composition

logger = logging.getLogger(__name__)


class User(AbstractUser):
    ADMIN = 0
    DOCTOR = 1
    PATIENT = 2
    VENDOR = 3
    PHARMACIST = 4
    ACCOUNT_TYPES = (
        (ADMIN, "Admin"), (DOCTOR, "Doctor"), (PATIENT, "Patient"), (VENDOR, "Vendor"), (PHARMACIST, "Pharmacist"))
    mobile_number = models.BigIntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    aadhar_number = models.BigIntegerField(null=True, blank=True, unique=True)
    medical_board_number = models.CharField(max_length=1000, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=PATIENT)
    pin = models.IntegerField(max_length=4, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def get_patient_prescription(self):
        schedules = []
        for slot in Item.SLOT_CHOICES:
            compositions = Item.objects.filter(prescription__patient=self, slot=slot[0]).values(
                'composition').distinct()
            data = []
            for composition in compositions:
                composition = Composition.objects.get(id=composition['composition'])
                schedule = Item.objects.filter(prescription__patient=self, slot=slot[0],
                                               composition=composition)
                total = schedule.aggregate(Sum("qty"))['qty__sum']
                data.append({'composition': composition.name, 'quantity': total})
            schedules.append({'data': data, 'slot': slot})
        return schedules

    def get_patient_prescription_dispense(self):
        data = []
        compositions = Item.objects.filter(prescription__patient=self).values(
            'composition').distinct()
        for composition in compositions:
            composition = Composition.objects.get(id=composition['composition'])
            schedules = Item.objects.filter(prescription__patient=self,
                                            composition=composition)
            total = 0
            for schedule in schedules:
                total += schedule.qty * schedule.no_of_days
            data.append({'composition': composition.name, 'quantity': total})
        return data

    def __str__(self):
        return self.first_name + "-" + str(self.aadhar_number)

    def __unicode__(self):
        return self.first_name + "-" + str(self.aadhar_number)


class Consumption(models.Model):
    patient = models.ForeignKey(User, limit_choices_to={'account_type': User.PATIENT})
    item = models.ForeignKey('doctor.Item', related_name='consumptions')
    consumed = models.BooleanField(default=False)
    medicine = models.ForeignKey('doctor.Medicine', related_name='consumptions')
    dispense_log = models.ForeignKey('dispenser.DispenseLog', related_name='consumptions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()


class Transaction(models.Model):
    amount = models.FloatField()
    email = models.EmailField(null=True, blank=True)
    purpose = models.TextField(null=True, blank=True)
    buyer_name = models.CharField(max_length=1000, null=True, blank=True)
    buyer_phone = models.BigIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=1000, null=True, blank=True)
    fees = models.FloatField(null=True, blank=True)
    long_url = models.TextField(null=True, blank=True)
    short_url = models.CharField(max_length=1000, blank=True, null=True)
    mac = models.TextField(null=True, blank=True)
    sms_status = models.CharField(max_length=100, null=True, blank=True)
    email_status = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.CharField(max_length=1000, null=True, blank=True)
    payment_request_id = models.CharField(max_length=100, null=True, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

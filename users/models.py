# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from doctor.models import CustomManager


class User(AbstractUser):
    ADMIN = 0
    DOCTOR = 1
    PATIENT = 2
    VENDOR = 3
    ACCOUNT_TYPES = ((ADMIN, "Admin"), (DOCTOR, "Doctor"), (PATIENT, "Patient"), (VENDOR, "Vendor"))
    mobile_number = models.BigIntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    aadhar_number = models.BigIntegerField(null=True, blank=True)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=PATIENT)
    profile_pic = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True,blank=True)


class ConsumptionLog(models.Model):
    patient = models.ForeignKey(User, limit_choices_to={'account_type': User.PATIENT})
    schedule = models.ForeignKey('doctor.Schedule', related_name='consumptions')
    consumed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True,blank=True)
    objects = CustomManager()

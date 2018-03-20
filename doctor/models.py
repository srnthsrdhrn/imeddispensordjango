# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.


class CustomManager(models.Manager):
    def get_queryset(self):
        return super(CustomManager, self).get_queryset().filter(deleted_at__isnull=True)


class Composition(models.Model):
    name = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()


class Medicine(models.Model):
    composition = models.ForeignKey(Composition, related_name='medicines', limit_choices_to={'deleted_at': None})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()


class Prescription(models.Model):
    doctor = models.ForeignKey('users.User', limit_choices_to={'account_type': 1},
                               related_name='doctor_prescriptions')
    patient = models.ForeignKey('users.User', limit_choices_to={'account_type': 2},
                                related_name='patient_prescriptions')
    doctor_note = models.TextField(null=True, blank=True, help_text='Doctor Note')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()

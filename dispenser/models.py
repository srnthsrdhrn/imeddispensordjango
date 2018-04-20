# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from doctor.models import Medicine, Prescription, CustomManager, Composition


class Device(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class Chamber(models.Model):
    device = models.ForeignKey('Device', related_name='chambers')
    medicine = models.ForeignKey(Medicine, null=True, blank=True, related_name='chambers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()


class DispenseLog(models.Model):
    medicine = models.ManyToManyField(Medicine, related_name='dispenses')
    qty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

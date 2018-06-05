# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from doctor.models import Medicine, Prescription, CustomManager, Composition
from users.models import User


class Device(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class Chamber(models.Model):
    chamber_number = models.IntegerField(default=0)
    device = models.ForeignKey('Device', related_name='chambers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()


class DispenseLog(models.Model):
    device = models.ForeignKey('Device', related_name='dispenses')
    prescription = models.ForeignKey('doctor.Prescription', related_name='dispenses')
    medicine = models.ManyToManyField(Medicine, related_name='dispenses')
    qty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomManager()


class Load(models.Model):
    device = models.ForeignKey(Device, related_name='loads')
    vendor = models.ForeignKey(User, related_name='vendor_loads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LoadData(models.Model):
    load = models.ForeignKey(Load, related_name='load_data')
    medicine = models.ForeignKey(Medicine, related_name='loads')
    quantity = models.IntegerField(default=0)
    chamber = models.ForeignKey(Chamber, related_name='loads')
    rate = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from doctor.models import Medicine, Prescription, CustomManager, Composition
from users.models import User


class Device(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey('users.User', related_name='machines_managing',
                               limit_choices_to={'account_type': User.VENDOR})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return ("\nlat:" + str(self.lat) + "\nlng:" + str(self.lng) + "\nLocation:" + self.location + "\n")


class Chamber(models.Model):
    VACUUM = 0
    ROLLER = 1
    SPRING = 2
    CHAMBER_TYPES = ((VACUUM, "Vacuum"), (ROLLER, "Roller"), (SPRING, "Spring"))
    type = models.IntegerField(choices=CHAMBER_TYPES)
    name = models.CharField(max_length=1000)
    device = models.ForeignKey('Device', related_name='chambers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return self.name + " " + self.get_type_display()


class DispenseLog(models.Model):
    chamber = models.ForeignKey('Chamber', related_name='dispenses')
    prescription = models.ForeignKey('doctor.Prescription', related_name='dispenses', null=True, blank=True)
    medicine = models.ForeignKey(Medicine, related_name='dispenses')
    quantity = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    actual_composition = models.ForeignKey('doctor.Composition', related_name='changed_dispenses', null=True,
                                           blank=True)
    load_data = models.ForeignKey('LoadData', related_name='dispenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomManager()


class Load(models.Model):
    device = models.ForeignKey(Device, related_name='loads')
    vendor = models.ForeignKey(User, related_name='vendor_loads')
    dispensed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LoadData(models.Model):
    load = models.ForeignKey(Load, related_name='load_data')
    medicine = models.ForeignKey(Medicine, related_name='loads')
    quantity = models.IntegerField(default=0)
    chamber = models.ForeignKey(Chamber, related_name='loads')
    rate = models.IntegerField(null=True,
                               blank=True)  # Vacuum rate is 1, other chambers, depending upon the amount of medicine in each strip
    expiry_date = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)
    expired_qty = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Medicine: " + self.medicine.__str__() + " Qty: " + str(
            self.quantity) + " Chamber: " + self.chamber.__str__()

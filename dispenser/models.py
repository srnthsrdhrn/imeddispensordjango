# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from doctor.models import Medicine, Prescription, CustomManager


class Device(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)


class Chamber(models.Model):
    device = models.ForeignKey('Device', related_name='chambers')
    medicine = models.ForeignKey(Medicine, null=True, blank=True, related_name='chambers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()


class Schedule(models.Model):
    BEFORE_BREAKFAST = 0
    AFTER_BREAKFAST = 1
    BEFORE_LUNCH = 2
    AFTER_LUNCH = 3
    BEFORE_DINNER = 4
    AFTER_DINNER = 5

    SLOT_CHOICES = (
        (BEFORE_BREAKFAST, "Before Breakfast"), (AFTER_BREAKFAST, "After Breakfast"), (BEFORE_LUNCH, "Before Lunch"),
        (AFTER_LUNCH, "After Lunch"), (BEFORE_DINNER, "Before Dinner"), (AFTER_DINNER, "After Dinner"))
    prescription = models.ForeignKey(Prescription, related_name='schedules')
    medicine = models.ForeignKey(Medicine, related_name='schedules')
    slot = models.IntegerField(choices=SLOT_CHOICES, default=BEFORE_BREAKFAST)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()


class DispenseLog(models.Model):
    prescription = models.ForeignKey(Prescription, related_name='dispenses')
    medicine = models.ManyToManyField(Medicine, related_name='dispenses')
    qty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = CustomManager()

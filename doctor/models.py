# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db import models


# Create your models here.

class CustomManager(models.Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set().filter(deleted_at__isnull=True)


class Composition(models.Model):
    name = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return self.name


class Medicine(models.Model):
    composition = models.ForeignKey(Composition, related_name='medicines', limit_choices_to={'deleted_at': None})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()


class Prescription(models.Model):
    doctor = models.ForeignKey('users.User', limit_choices_to={'account_type': 1},
                               related_name='doctor_prescriptions')
    patient = models.ForeignKey('users.User', limit_choices_to={'account_type': 2},
                                related_name='patient_prescriptions')
    doctor_note = models.TextField(null=True, blank=True, help_text='Doctor Note')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return self.doctor_note


class ScheduleManager(models.Manager):
    def get_query_set(self):
        days = (datetime.now() - self.created_at).days
        super(ScheduleManager, self).get_query_set().filter(no_of_days__lte=days)


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
    composition = models.ForeignKey(Composition, related_name='schedules')
    slot = models.IntegerField(choices=SLOT_CHOICES, default=BEFORE_BREAKFAST)
    qty = models.IntegerField(default=0)
    no_of_days = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    objects = ScheduleManager()

    def __str__(self):
        return self.composition.__str__()

    def get_slot(self):
        return self.SLOT_CHOICES[self.slot][1]

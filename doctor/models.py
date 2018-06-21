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
    dosage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return self.name + " " + str(self.dosage) + "mg"


class Medicine(models.Model):
    name = models.CharField(max_length=1000)
    composition = models.ForeignKey(Composition, related_name='medicines', limit_choices_to={'deleted_at': None})
    price = models.FloatField(null=True, blank=True)
    otc = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return self.name + " " + str(self.composition.dosage) + "mg"


class Prescription(models.Model):
    doctor = models.ForeignKey('users.User', limit_choices_to={'account_type': 1},
                               related_name='doctor_prescriptions')
    patient = models.ForeignKey('users.User', limit_choices_to={'account_type': 2},
                                related_name='patient_prescriptions')
    doctor_note = models.TextField(null=True, blank=True, help_text='Doctor Note')
    scanned_copy = models.ImageField(null=True, blank=True)
    pharmacist = models.ForeignKey('users.User', related_name='prescriptions_uploaded', null=True, blank=True)
    dispensed = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = CustomManager()

    def __str__(self):
        return "Doctor: " + self.doctor.first_name + " Patient: " + self.patient.first_name


class ItemManager(models.Manager):
    def get_query_set(self):
        days = (datetime.now() - self.created_at).days
        super(ItemManager, self).get_query_set().filter(no_of_days__lte=days)


class Item(models.Model):
    BEFORE_BREAKFAST = 0
    AFTER_BREAKFAST = 1
    BEFORE_LUNCH = 2
    AFTER_LUNCH = 3
    BEFORE_DINNER = 4
    AFTER_DINNER = 5

    SLOT_CHOICES = (
        (BEFORE_BREAKFAST, "Before Breakfast"), (AFTER_BREAKFAST, "After Breakfast"), (BEFORE_LUNCH, "Before Lunch"),
        (AFTER_LUNCH, "After Lunch"), (BEFORE_DINNER, "Before Dinner"), (AFTER_DINNER, "After Dinner"))
    composition = models.ForeignKey('Composition', related_name='prescribed_list')
    prescription = models.ForeignKey('Prescription', related_name='items')
    quantity = models.IntegerField()
    slot = models.IntegerField(choices=SLOT_CHOICES)
    no_of_days = models.IntegerField(default=1)
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True,blank=True)
    objects = ItemManager()

    def __str__(self):
        return "Prescription: " + self.prescription.__str__() + " Composition: " + self.composition.__str__() + " " + self.get_slot_display()

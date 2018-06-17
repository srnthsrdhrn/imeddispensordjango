from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Recharge(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey('users.User', related_name='refills')
    cashier = models.ForeignKey('users.User', related_name='recharges')
    invoice_id = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

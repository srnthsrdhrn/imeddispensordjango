# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.db.models import Sum

from MedicalDispenser import settings
from MedicalDispenser.multi import chain, check_call
from doctor.models import CustomManager, Item, Prescription, Composition

logger = logging.getLogger(__name__)


class Transaction(models.Model):
    # Options for transaction type
    KASH_DEPOSIT = 0
    CASH_DEPOSIT = 1
    WALLET_TRANSACTION = 2
    USER_KASH_REFUND = 3
    USER_KASH_PAYMENT = 4
    USER_CASH_PAYMENT = 5
    VENDOR_KASH_CREDIT = 6
    VENDOR_CASH_DEBIT = 7
    CASH_TRANSFER = 8

    TRANSACTION_CHOICES = (
        (KASH_DEPOSIT, "Recharge"), (CASH_DEPOSIT, "Cashier Debit"), (WALLET_TRANSACTION, "Friendly Transfer"),
        (USER_KASH_REFUND, "Vendor Refund"), (USER_KASH_PAYMENT, "User Payment"),
        (USER_CASH_PAYMENT, "Cash Payment"), (VENDOR_KASH_CREDIT, "Vendor Credit"),
        (VENDOR_CASH_DEBIT, "Vendor Settlement"), (CASH_TRANSFER, "Sub Cashier to Main Cashier Transfer"))
    sender = models.ForeignKey("users.User", related_name='sent_transactions')
    receiver = models.ForeignKey("users.User", related_name='received_transactions')
    amount = models.FloatField()
    transaction_type = models.IntegerField(choices=TRANSACTION_CHOICES)
    transaction_hash = models.CharField(max_length=1024, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=PATIENT)
    pin = models.IntegerField(max_length=4)
    wallet_address = models.CharField(max_length=1024, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def create_wallet(self):
        if self.wallet_address == '':
            self.wallet_address = chain.getnewaddress()
            self.save()

    def burn_asset(self, amount, main_cashier):
        try:

            transaction = chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                              settings.MULTICHAIN_ASSET, amount)
            transaction_object = Transaction.objects.create(sender=self, receiver=main_cashier, amount=amount,
                                                            transaction_type=Transaction.VENDOR_KASH_CREDIT,
                                                            transaction_hash=transaction)
            wallet_balance = WalletBalance.objects.create(user=self, balance=self.get_wallet_balance(),
                                                          transaction=transaction_object)
            wallet_balance.save()
            if check_call(transaction):
                pass
            else:
                logger.error(transaction["error"])
        except:
            logger.error("Multichain call failing")

    def issue_asset(self, amount, sender):
        amount = float(amount)
        try:
            receiver_balance = self.get_wallet_balance()
            if receiver_balance < 0:
                balance = receiver_balance + amount
                if balance < 0:
                    transaction = chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                                      settings.MULTICHAIN_ASSET_NKASH, amount)
                else:
                    chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                        settings.MULTICHAIN_ASSET_NKASH, -receiver_balance)
                    transaction = chain.issuemore(self.wallet_address, settings.MULTICHAIN_ASSET, balance)
            else:
                transaction = chain.issuemore(self.wallet_address, settings.MULTICHAIN_ASSET, amount)
            if check_call(transaction):
                transaction_object = Transaction.objects.create(sender=sender, receiver=self, amount=amount,
                                                                transaction_type=Transaction.KASH_DEPOSIT,
                                                                transaction_hash=transaction)
                wallet_balance = WalletBalance.objects.create(user=self, balance=self.get_wallet_balance(),
                                                              transaction=transaction_object)
                wallet_balance.save()
                return True
            else:
                logger.error(transaction['error'])
                return False
        except Exception as inst:
            logger.error("Multichain call failing" + inst.__str__())
            return False

    def issue_nkash(self, amount, sender):
        # Amount Should be given in Positive Only
        balance = self.get_wallet_balance()
        if balance > 0:
            # debt = balance - amount
            # if debt < 0:
            #     debt = -debt
            #     transaction = chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
            #                                       settings.MULTICHAIN_ASSET, balance)
            #     chain.issuemore(self.wallet_address, settings.MULTICHAIN_ASSET_NKASH, debt)
            # else:
            #     transaction = chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
            #                                       settings.MULTICHAIN_ASSET,
            #                                       amount)
            return False
        else:
            transaction = chain.issuemore(self.wallet_address, settings.MULTICHAIN_ASSET_NKASH, amount)
        if check_call(transaction):
            transaction = Transaction.objects.create(sender=self, receiver=sender, amount=-amount,
                                                     transaction_type=Transaction.KASH_DEPOSIT,
                                                     transaction_hash=transaction)
            wallet_balance = WalletBalance.objects.create(user=self, balance=self.get_wallet_balance(),
                                                          transaction=transaction)
            wallet_balance.save()
            return transaction
        else:
            logger.error(transaction['error'])
            return False

    def get_wallet_balance(self):
        if not self.wallet_address.strip():
            logging.error("User wallet address is not configured user_id:%s" % self.id)
            return 0
        else:
            try:
                balances = chain.getaddressbalances(self.wallet_address)
                if check_call(balances):
                    for asset in balances:
                        if asset['name'] == settings.MULTICHAIN_ASSET_NKASH:
                            if asset['qty'] > 0:
                                return -asset['qty']
                            else:
                                continue
                        elif asset['name'] == settings.MULTICHAIN_ASSET:
                            if asset['qty'] > 0:
                                return asset['qty']
                            else:
                                continue
                    return 0
                logger.error(balances['error'])
            except Exception:
                logger.error(Exception)
            return False

    # This function deals both User to User Transfer and Vendor Refund.
    # It performs User to User Transfer by Default.
    # For Vendor Refund specify the transaction_type as USER_KASH_REFUND
    def transfer_to_user(self, user, amount, transaction_type=Transaction.WALLET_TRANSACTION):
        receiver_balance = user.get_wallet_balance()
        if receiver_balance < 0:
            balance = receiver_balance + amount
            if balance < 0:
                transaction = chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                                  settings.MULTICHAIN_ASSET, amount)
                chain.sendassetfrom(user.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                    settings.MULTICHAIN_ASSET_NKASH, amount)
            else:
                chain.sendassetfrom(self.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                    settings.MULTICHAIN_ASSET, -receiver_balance)
                chain.sendassetfrom(user.wallet_address, settings.MULTICHAIN_BURN_ADDRESS,
                                    settings.MULTICHAIN_ASSET_NKASH, -receiver_balance)
                transaction = chain.sendassetfrom(self.wallet_address, user.wallet_address,
                                                  settings.MULTICHAIN_ASSET, balance)

        else:
            transaction = chain.sendassetfrom(self.wallet_address, user.wallet_address, settings.MULTICHAIN_ASSET,
                                              amount)
        if check_call(transaction):
            transaction_object = Transaction.objects.create(sender=self, receiver=user, amount=amount,
                                                            transaction_type=transaction_type,
                                                            transaction_hash=transaction)
            wallet_balance = WalletBalance.objects.create(user=self, balance=self.get_wallet_balance(),
                                                          transaction=transaction_object)
            wallet_balance.save()
            wallet_balance1 = WalletBalance.objects.create(user=user, balance=user.get_wallet_balance(),
                                                           transaction=transaction_object)
            wallet_balance1.save()
            return transaction_object, "No Error"
        else:
            logger.error(transaction['error'])
            return False, transaction['error']

    def pay_vendor(self, vendor, amount):
        transaction = chain.sendassetfrom(self.wallet_address, vendor.wallet_address, settings.MULTICHAIN_ASSET,
                                          amount)
        if check_call(transaction):
            transaction = Transaction.objects.create(sender=self, receiver=vendor, amount=amount,
                                                     transaction_type=Transaction.USER_KASH_PAYMENT,
                                                     transaction_hash=transaction)
            wallet_balance = WalletBalance.objects.create(user=self, balance=self.get_wallet_balance(),
                                                          transaction=transaction)
            wallet_balance.save()
            wallet_balance1 = WalletBalance.objects.create(user=vendor, balance=vendor.get_wallet_balance(),
                                                           transaction=transaction)
            wallet_balance1.save()
            return transaction

        else:
            logger.error(transaction['error'])
        return False

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)
        self._pin = raw_pin

    def check_pin(self, raw_pin):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_pin):
            self.set_pin(raw_pin)
            # Password hash upgrades shouldn't be considered password changes.
            self._pin = None
            self.save(update_fields=["pin"])

        return check_password(raw_pin, self.pin, setter)

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


class WalletBalance(models.Model):
    user = models.ForeignKey(User)
    balance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey('users.Transaction')


class Invoice(models.Model):
    vendor = models.ForeignKey("users.User", related_name='sale_invoices')
    user = models.ForeignKey("users.User", related_name='invoices')
    total = models.FloatField(default=0)
    invoice_state = models.IntegerField()
    transaction = models.ForeignKey("Transaction", blank=True, null=True)
    order_hash = models.CharField(max_length=1024, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_by = models.ForeignKey("users.User", default=None, null=True)
    refund = models.ForeignKey("users.Refund_details", blank=True, null=True, related_name='refund_object')
    is_preordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# part of the invoice
class LineItems(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="line_items")
    medicine = models.ForeignKey("doctor.Medicine", related_name='purchases')
    name = models.CharField(max_length=255)
    price = models.FloatField()
    cost_price = models.FloatField()
    qty = models.IntegerField()
    total = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Deposit(models.Model):
    deposit_amount = models.FloatField(help_text="Amount to be Deposited")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(help_text="Details of the amount deposited If needed", blank=True, null=True)


class Refund_details(models.Model):
    transaction = models.ForeignKey("users.Transaction", default=None, null=True, related_name='refund_transaction')
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

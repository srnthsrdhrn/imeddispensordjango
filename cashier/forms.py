from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from cashier.models import Recharge
from users.models import User


class RechargeForm(forms.Form):
    amount = forms.CharField()
    aadhar_number = forms.CharField(widget=forms.PasswordInput)
    invoice_id = forms.CharField(max_length=1000, label='Bill Invoice Number',
                                 help_text='Enter the Invoice Number of the Bill Got from the Cashier')

    def __init__(self, *args, **kwargs):
        self.cashier = kwargs.pop("cashier", None)
        super(RechargeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit("submit", "Submit"))

    def is_valid(self):
        is_valid = super(RechargeForm, self).is_valid()

        if not is_valid:
            return is_valid
        data = self.cleaned_data
        try:
            User.objects.get(aadhar_number=data.get("aadhar_number"))
        except User.DoesNotExist:
            self.add_error('aadhar_number', 'The User does not exist!')
            is_valid = False

        return is_valid

    def save(self):
        data = self.data
        user = User.objects.get(aadhar_number=data.get("aadhar_number"))
        amount = float(data.get("amount"))
        check1 = user.issue_asset(amount, self.cashier)
        # check2 = self.cashier.issue_cash(amount, user)
        if check1:
            recharge = Recharge.objects.create(user=user, cashier=self.cashier,
                                               invoice_id=self.cleaned_data['invoice_id'],
                                               amount=float(amount))

            return True
        return False


class BalanceForm(forms.Form):
    aadhar_number = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.cashier = kwargs.pop("cashier", None)
        super(BalanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit("submit", "Submit"))

    def is_valid(self):
        is_valid = super(BalanceForm, self).is_valid()

        if not is_valid:
            return is_valid
        data = self.cleaned_data
        try:
            User.objects.get(aadhar_number=data.get("aadhar_number"))
        except User.DoesNotExist:
            self.add_error('aadhar_number', 'The User does not exist!')
            is_valid = False
        return is_valid

    def save(self):
        data = self.data
        user = User.objects.get(aadhar_number=data.get("aadhar_number"))
        return user

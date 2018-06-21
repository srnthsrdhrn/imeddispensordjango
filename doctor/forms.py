from crispy_forms.helper import FormHelper
from dal import autocomplete
from django import forms

from doctor.models import Composition
from users.models import User


class DiagnosisForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DiagnosisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

    composition = forms.ModelChoiceField(queryset=Composition.objects.all(),
                                         empty_label='No Composition Added',
                                         widget=autocomplete.ModelSelect2(url='composition_autocomplete',
                                                                          attrs={'onchange': 'javascript:show();'}))
    description = forms.CharField(max_length=1000)


class PharmacistDiagnosisForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PharmacistDiagnosisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

    composition = forms.ModelChoiceField(queryset=Composition.objects.all(),
                                         empty_label='No Composition Added',
                                         widget=autocomplete.ModelSelect2(url='composition_autocomplete',
                                                                          attrs={'onchange': 'javascript:show();'}))
    description = forms.CharField(max_length=1000)
    patient = forms.ModelChoiceField(queryset=User.objects.filter(account_type=User.PATIENT),
                                     empty_label='No Patients Added',
                                     widget=autocomplete.ModelSelect2(url='patient_auto_complete'))

    doctor = forms.ModelChoiceField(queryset=User.objects.filter(account_type=User.PATIENT),
                                    empty_label='No Doctors Added',
                                    widget=autocomplete.ModelSelect2(url='doctor_auto_complete'))
    prescription_image = forms.ImageField()

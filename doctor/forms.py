from crispy_forms.helper import FormHelper
from dal import autocomplete
from django import forms

from doctor.models import Composition


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

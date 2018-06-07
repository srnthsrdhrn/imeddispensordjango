from django import forms
from .models import Device
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class PostForm(forms.ModelForm):
    helper=FormHelper()
    helper.form_method='POST'
    helper.add_input(Submit('submit','submit',css_class='btn_primary'))


    class Meta:
        model = Device
        fields = ('id','lat','lng','location','vendor')

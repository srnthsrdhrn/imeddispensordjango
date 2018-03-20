from django import forms

from doctor.models import Composition


class DiagnosisForm(forms.Form):
    composition = forms.ModelMultipleChoiceField(queryset=Composition.objects.all())
    description = forms.CharField(max_length=1000)

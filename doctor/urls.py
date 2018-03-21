from django.conf.urls import url

from doctor.api_views import CompositionAutoComplete, CompositionList, CompletePrescription
from doctor.views import dashboard, new_diagnosis, check_patient

urlpatterns = [
    url(r'^dashboard$', dashboard, name='doctor_dashboard'),
    url(r'^new_diagnosis/(?P<patient_id>[0-9]+)$', new_diagnosis, name='new_diagnosis'),
    url(r'^composition_autocomplete$', CompositionAutoComplete.as_view(), name='composition_autocomplete'),
    url(r'^composition_list$', CompositionList.as_view(), name='composition_list'),
    url(r'^complete_prescription$', CompletePrescription.as_view(), name='complete_prescription'),
    url(r'^check_patient$', check_patient, name='check_patient'),
]

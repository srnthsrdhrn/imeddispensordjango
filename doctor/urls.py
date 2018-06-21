from django.conf.urls import url

from doctor.api_views import CompositionAutoComplete, CompositionList, CompletePrescription, PatientAutoComplete, \
    DoctorAutoComplete, OTCMedicineListAPI
from doctor.views import dashboard, new_diagnosis, check_patient, patient_list, prescription_view, \
    patient_prescription_view, pharmacist_prescription_upload, complete_pharmacist_prescription

urlpatterns = [
    url(r'^dashboard$', dashboard, name='doctor_dashboard'),
    url(r'^new_diagnosis/(?P<patient_id>[0-9]+)$', new_diagnosis, name='new_diagnosis'),
    url(r'^composition_autocomplete$', CompositionAutoComplete.as_view(), name='composition_autocomplete'),
    url(r'^patient_autocomplete$', PatientAutoComplete.as_view(), name='patient_auto_complete'),
    url(r'^doctor_auto_complete', DoctorAutoComplete.as_view(), name='doctor_auto_complete'),
    url(r'^composition_list$', CompositionList.as_view(), name='composition_list'),
    url(r'^complete_prescription$', CompletePrescription.as_view(), name='complete_prescription'),
    url(r'^check_patient$', check_patient, name='check_patient'),
    url(r'^patient_list$', patient_list, name='patient_list'),
    url(r'^prescription/(?P<prescription_id>[0-9]+)', prescription_view, name='prescription_view'),
    url(r'^prescription_list/(?P<patient_id>[0-9]+)', patient_prescription_view, name='patient_prescription_view'),
    url(r'^pharmacist_prescription$', pharmacist_prescription_upload, name='pharmacist_prescription_upload'),
    url(r'^complete_pharmacist_prescription$', complete_pharmacist_prescription,
        name='complete_pharmacist_prescription'),
    url(r'^otc_medicine_list$', OTCMedicineListAPI.as_view(), name='otc_medicine_list'),
]

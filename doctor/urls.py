from django.conf.urls import url

from doctor.views import dashboard, new_diagnosis

urlpatterns = [
    url(r'^dashboard$', dashboard, name='doctor_dashboard'),
    url(r'^new_diagnosis$', new_diagnosis, name='new_diagnosis'),
]

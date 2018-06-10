"""MedicalDispenser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout

from dispenser.views import VendorLoadAPI, DeviceDetails, DispenseLogAPI
from doctor.api_views import UserPrescriptionAPI, UserDetailAPI, PrescriptionAPI, MedicineListAPI
from users.views import landing_page, login_success, LoginAPI, PrescriptionAPI as prescription, DeviceAuthenticate, \
    access_pi

urlpatterns = [
    url(r'^$', landing_page, name='landing_page'),
    url(r'^admin/', admin.site.urls),
    url(r'^access_pi', access_pi),
    url(r'^users/', include('users.urls')),
    url(r'^login', login, name='login'),
    url(r'^logout', logout, name='logout'),
    url(r'^accounts/profile/$', login_success),
    url(r'^doctor/', include('doctor.urls')),
    url(r'^api/v1/login', LoginAPI.as_view()),
    url(r'^api/v1/authenticate', DeviceAuthenticate.as_view()),
    url(r'^api/v1/user_prescription', UserPrescriptionAPI.as_view()),
    url(r'^api/v1/user_details', UserDetailAPI.as_view()),
    url(r'^api/v1/prescription', PrescriptionAPI.as_view()),
    url(r'^api/v1/user_1_prescription', prescription.as_view()),
    url(r'^api/v1/load', VendorLoadAPI.as_view()),
    url(r'^api/v1/device_data', DeviceDetails.as_view()),
    url(r'^api/v1/medicine_list', MedicineListAPI.as_view()),
    url(r'^api/v1/dispense_log', DispenseLogAPI.as_view()),
    url(r'^dispenser/', include('dispenser.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^device_list$', views.device_list, name='devices_list'),
    url(r'^insert/', views.post_new, name='insert_device'),
    url(r'^device_load/(?P<device_id>[0-9]+)', views.vendor_load_device, name='device_load')
]

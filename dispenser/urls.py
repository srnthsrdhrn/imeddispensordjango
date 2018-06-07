from django.conf.urls import include,url
from . import views

urlpatterns = [
    url(r'^$',views.Dev, name='devices'),
    url(r'^insert/',views.post_new,name='insert'),
]

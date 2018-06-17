from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^recharge/$', views.recharge, name='cashier_recharge'),
    url(r'^balance/$', views.view_balance, name='cashier_balance'),

]

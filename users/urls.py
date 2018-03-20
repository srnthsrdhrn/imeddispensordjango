from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^dashboard$', views.login_success, name='user_dashboard'),
]

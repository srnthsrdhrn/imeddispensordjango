from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^dashboard$', views.login_success, name='user_dashboard'),
    url(r'^store_session$', views.StoreSession.as_view(), name='store_session'),
    url(r'^api/v1/payment_webhook', views.InstaMojoWebhook.as_view()),
    url(r'^api/v1/initialize_payment', views.InitiatePayment.as_view()),
    url(r'^api/v1/check_payment', views.PaymentVerification.as_view()),
]

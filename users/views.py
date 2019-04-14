# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from instamojo import create_payment_request
from users.models import User, Transaction
from users.serializers import PrescriptionSerializer, UserSerializer


def landing_page(request):
    return render(request, 'theme/index.html')


def login_success(request):
    if request.user.account_type == User.DOCTOR or request.user.account_type == User.VENDOR:
        return redirect('doctor_dashboard')
    # elif request.user.account_type == User.PATIENT:
    #     return redirect('patient_dashboard')
    return render(request, 'admin_theme/dashboard.html')


@login_required
def patient_dashboard(request):
    user = request.user
    transactions = Transaction.objects.filter(sender=user)
    return render(request, 'patient/patient_dashboard.html', {'transactions': transactions})


class LoginAPI(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                if user.account_type == User.VENDOR:
                    data = UserSerializer(user).data
                    data['vendor_id'] = 'vendor-' + str(user.id)
                    return Response(data)
                else:
                    return Response(UserSerializer(user).data)
            else:
                return Response({'status': 'Username or Password Wrong'}, status=400)
        except User.DoesNotExist, e:
            return Response({'status': 'User does not exists'}, status=400)


class DeviceAuthenticate(APIView):
    def post(self, request):
        aadhar = request.POST.get("aadhar")
        pin = request.POST.get("pin")
        user = User.objects.get(aadhar_number=aadhar)
        try:
            if user.pin == int(pin):
                return Response(UserSerializer(user).data)
            else:
                return Response({'error': 'Wrong Credentials'}, status=400)
        except Exception, e:
            return Response({'error': 'Error in Request ' + e.message}, status=400)


class PrescriptionAPI(APIView):
    def get(self, request):
        aadhar = request.GET.get("aadhar")
        username = request.GET.get("username")
        try:
            user = User.objects.get(aadhar_number=aadhar)
            if user.username == username:
                prescriptions = user.patient_prescriptions.all().order_by('-created_at')
                return Response(PrescriptionSerializer(prescriptions, many=True).data)
            else:
                return Response({'status': "Wrong Data"})
        except User.DoesNotExist, e:
            return Response({'status': 'User Does Not Exist'}, status=400)


class StoreSession(APIView):
    def get(self, request):
        link = request.GET.get("link")
        if link:
            f = open("link_storage.txt", "w")
            f.write(link)
            return Response({"success": "Stored"})
        else:
            return Response({"error": "Link Missing"}, status=400)


def access_pi(request):
    f = open("link_storage.txt")
    link = f.read()
    return redirect(link)


class ScheduleAPI(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        aadhar = request.GET.get("aadhar")
        if user_id and aadhar:
            user = User.objects.get(id=user_id)
            if user.aadhar_number == aadhar:
                pass
            else:
                return Response({"status": "Wrong Credentials"}, status=400)


class InstaMojoWebhook(APIView):
    def post(self, request):
        data = request.POST
        request_id = data.get("payment_request_id")
        transaction = Transaction.objects.get(payment_request_id=request_id)
        transaction.payment_id = data.get("payment_id")
        transaction.short_url = data.get("short_url")
        transaction.currency = data.get("currency")
        transaction.paid = True
        transaction.fees = data.get("fees")
        transaction.email = data.get("buyer")
        transaction.buyer_name = data.get("buyer_name")
        transaction.save()
        return Response({"Success"})
        # mac_provided = data.get("mac")
        # message = "|".join(v for k, v in sorted(data.items(), key=lambda x: x[0].lower()) if k != 'mac')
        # mac_calculated = hmac.new(INSTA_MOJO_SALT_TEST, message, hashlib.sha1).hexdigest()
        # if mac_provided == mac_calculated:
        #     if data['status'] == "Credit":
        #         print("Success")
        #         # Payment was successful, mark it as completed in your database.
        #         pass
        #     else:
        #         print("Error")
        #         pass
        #     # Payment was unsuccessful, mark it as failed in your database.
        #     return Response({"status": "Success"})
        # else:
        #     return Response({"status": "Error"}, status=400)


class InitiatePayment(APIView):
    def post(self, request):
        data = request.POST
        user_id = data.get("user_id")
        aadhar = data.get("aadhar")
        amount = data.get("amount")
        mobile_number = data.get("mobile_number")
        # if aadhar and user_id:
        #     user = User.objects.get(id=user_id)
        #     if user.aadhar_number == int(aadhar):
        #         response = create_payment_request("Medicine Purchase", amount=str(amount), buyer_name=user.first_name,
        #                                           email=user.email,
        #                                           phone=str(user.mobile_number))
        #         if response:
        #             transaction = Transaction()
        #             transaction.email = response.get("email")
        #             transaction.payment_request_id = response.get("id")
        #             transaction.buyer_phone = response.get("phone")
        #             transaction.sender = user
        #             transaction.amount = response.get("amount")
        #             transaction.sms_status = response.get("sms_status")
        #             transaction.email_status = response.get("email_status")
        #             transaction.long_url = response.get("longurl")
        #             transaction.purpose = response.get("purpose")
        #             transaction.save()
        #             return Response({"id": transaction.payment_request_id})
        #         else:
        #             return Response({"error": "Error Processing Request"})
        #     else:
        #         return Response({"error": "Wrong Credentials"}, status=400)
        # elif mobile_number and not aadhar:
        #     response = create_payment_request(purpose="Medicine Purchase", amount=str(amount), phone=mobile_number)
        #     if response:
        #         transaction = Transaction()
        #         transaction.payment_request_id = response.get("id")
        #         transaction.buyer_phone = response.get("phone")
        #         transaction.amount = response.get("amount")
        #         transaction.sms_status = response.get("sms_status")
        #         transaction.email_status = response.get("email_status")
        #         transaction.long_url = response.get("longurl")
        #         transaction.purpose = response.get("purpose")
        #         transaction.save()
        #         return Response({"id": transaction.payment_request_id})
        #     else:
        #         return Response({"error": "Error Processing Request"}, status=400)
        if user_id and aadhar:
            requests.post('https://imedkash.iqube.io/api/external_payment_gateway',
                          data={"user_id": user_id, "aadhar": aadhar, "qty": 3})
            return Response({"id": 1, "status": "Success"})
        else:
            return Response({"error": "Bad Request"}, status=400)


class PaymentVerification(APIView):
    def get(self, request):
        data = request.GET
        payment_request_id = data.get("payment_request_id")
        try:
            transaction = Transaction.objects.get(payment_request_id=payment_request_id)
        except Transaction.DoesNotExist, e:
            return Response({"error": "Invalid Payment Request ID"})
        return Response({"status": transaction.paid})
        # return Response({"status": True})


class PaymentOverride(APIView):
    def get(self, request):
        for t in Transaction.objects.all():
            t.paid = True
            t.save()
        return Response({"Successfully Overridden"})

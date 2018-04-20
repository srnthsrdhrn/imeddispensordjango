# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import PrescriptionSerializer, UserSerializer


def landing_page(request):
    return render(request, 'theme/index.html')


def login_success(request):
    if request.user.account_type == User.DOCTOR:
        return redirect('doctor_dashboard')
    return render(request, 'admin_theme/dashboard.html')


class LoginAPI(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return Response(UserSerializer(user).data)
            else:
                return Response({'status': 'Username or Password Wrong'}, status=400)
        except User.DoesNotExist, e:
            return Response({'status': 'User does not exists'}, status=400)


class PrescriptionAPI(APIView):
    def get(self, request):
        username = request.GET.get("username")
        user_id = request.GET.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            if user.username == username:
                prescriptions = user.patient_prescriptions.all().order_by('-created_at')
                return Response(PrescriptionSerializer(prescriptions, many=True).data)
            else:
                return Response({'status': "Wrong Data"})
        except User.DoesNotExist, e:
            return Response({'status': 'User Does Not Exist'}, status=400)

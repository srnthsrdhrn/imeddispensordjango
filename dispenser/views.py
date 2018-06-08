# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.dateparse import parse_datetime
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import Device, Chamber, Load, LoadData
from dispenser.serializers import DeviceSerializer, DispenseLogSerializer
from doctor.models import Medicine
from users.models import User


class VendorLoadAPI(APIView):
    def post(self, request):
        datas = request.data
        vendor_id = datas.get("vendor_id")
        device_id = datas.get("device_id")
        if vendor_id and device_id:
            device = Device.objects.get(id=device_id)
            vendor = User.objects.get(id=vendor_id)
            flag = Load.objects.filter(vendor=vendor, device=device, dispensed=False).exists()
            if flag:
                return Response({'message': "Device already loaded"})
            load = Load.objects.create(vendor=vendor, device=device)
            for data in datas.get("data"):
                medicine = data.get("medicine")
                medicine = Medicine.objects.get(id=medicine)
                quantity = data.get("quantity")
                chamber = data.get("chamber")
                expiry_date = data.get("expiry_date")
                expiry = parse_datetime(expiry_date)
                chamber = Chamber.objects.get(id=chamber)
                rate = data.get("rate")
                if rate:
                    LoadData.objects.create(chamber=chamber, medicine=medicine, quantity=quantity, load=load, rate=rate,
                                            expiry_date=expiry)
                else:
                    LoadData.objects.create(chamber=chamber, medicine=medicine, quantity=quantity, load=load,
                                            expiry_date=expiry)
            return Response({'status': "Success"})
        return Response({'status': 'Error Bad Request'}, status=400)


class DeviceDetails(APIView):
    def get(self, request):
        device_id = request.GET.get("device_id")
        device = Device.objects.get(id=device_id)
        return Response(DeviceSerializer(device).data)


class DispenseLogAPI(APIView):
    def post(self, request):
        datas = request.data
        DispenseLogSerializer(data=datas, many=True).save()

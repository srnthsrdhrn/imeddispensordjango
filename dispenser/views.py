# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import Device, Chamber, Load, LoadData
from dispenser.serializers import DeviceSerializer
from doctor.models import Medicine
from users.models import User


class VendorLoadAPI(APIView):
    def post(self, request):
        datas = request.data
        # datas = json.loads(datas)
        vendor_id = datas.get("vendor_id")
        device_id = datas.get("device_id")
        if vendor_id and device_id:
            device = Device.objects.get(id=device_id)
            vendor = User.objects.get(id=vendor_id)
            load = Load.objects.create(vendor=vendor, device=device)
            for data in datas.get("data"):
                medicine = data.get("medicine")
                medicine = Medicine.objects.get(id=medicine)
                quantity = data.get("quantity")
                chamber = data.get("chamber")
                chamber = Chamber.objects.get(id=chamber)
                rate = data.get("rate")
                if rate:
                    LoadData.objects.create(chamber=chamber, medicine=medicine, quantity=quantity, load=load, rate=rate)
                else:
                    LoadData.objects.create(chamber=chamber, medicine=medicine, quantity=quantity, load=load)
            return Response({'status': "Success"})
        return Response({'status': 'Error Bad Request'}, status=400)


class DeviceDetails(APIView):
    def get(self, request):
        device_id = request.GET.get("device_id")
        device = Device.objects.get(id=device_id)
        return Response(DeviceSerializer(device).data)

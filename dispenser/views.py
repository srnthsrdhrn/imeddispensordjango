# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import Device, Chamber, Load, LoadData
from doctor.models import Medicine
from users.models import User


class VendorLoadAPI(APIView):
    def post(self, request):
        datas = request.POST
        datas = json.loads(datas)
        device_id = datas.get("device_id")
        device = Device.objects.get(id=device_id)
        vendor = User.objects.get(username='vendor')
        load = Load.objects.create(vendor=vendor, device=device)
        for id, data in enumerate(datas.get("data")):
            chamber = Chamber.objects.get(device=device, chamber_number=id)
            medicine = data.get("medicine")
            medicine = Medicine.objects.get(name=medicine)
            qty = data.get("qty")
            LoadData.objects.create(chamber=chamber, medicine=medicine, quantity=qty, load=load)
        return Response({'status': "Success"})
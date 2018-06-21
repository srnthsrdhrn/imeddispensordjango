# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import Device, Chamber, Load, LoadData, DispenseLog
from dispenser.serializers import DeviceSerializer
from doctor.models import Medicine, Prescription, Composition
from users.models import User
from .forms import PostForm


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


def device_list(request):
    dis = Device.objects.all()
    context = {"dis": dis, }
    return render(request, 'dispenser/dispenser.html', context)


def post_new(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            post.save()
            return HttpResponseRedirect('/dispenser/')
    else:
        form = PostForm()
    return render(request, 'dispenser/device_form.html', {'form': form})


class DispenseLogAPI(APIView):
    def post(self, request):
        datas = request.data
        try:
            for data in datas:
                prescription = data.get("prescription_id")
                medicine = data.get("medicine")
                actual_composition_id = data.get("actual_composition_id")
                quantity = int(data.get("quantity"))
                load_data = data.get("load_data")
                chamber = data.get("chamber_id")
                DispenseLog.objects.create(chamber_id=chamber, medicine_id=medicine, quantity=quantity,
                                           load_data_id=load_data,
                                           actual_composition_id=actual_composition_id, prescription_id=prescription)
                load_data = LoadData.objects.get(id=load_data)
                load_datas = load_data.load.load_data.all()
                flag = True
                for loaddata in load_datas:
                    available = loaddata.quantity
                    dispensed = loaddata.dispenses.all().aggregate(Sum("quantity"))['quantity__sum']
                    if available != dispensed:
                        flag = False
                if flag:
                    load = load_data.load
                    load.dispensed = True
                    load.save()
                if prescription:
                    prescription = Prescription.objects.get(id=prescription)
                    compositions = prescription.items.values('composition').distinct()
                    dispense_flag = True
                    for composition in compositions:
                        composition = composition['composition']
                        composition = Composition.objects.get(id=composition)
                        cmps = prescription.items.filter(composition=composition)
                        required_qty = 0
                        for cmp in cmps:
                            required_qty += cmp.quantity * cmp.no_of_days
                        dispensed_qty = 0
                        dosages = prescription.dispenses.filter(medicine__composition__name=composition.name).values(
                            'medicine__composition__dosage').distinct()
                        for dosage in dosages:
                            dosage = dosage['medicine__composition__dosage']
                            temp_dosage = dosage / float(composition.dosage)
                            temp_qty = \
                                prescription.dispenses.filter(medicine__composition__dosage=dosage,
                                                              medicine__composition__name=composition.name).distinct().aggregate(
                                    Sum("quantity"))['quantity__sum'] * temp_dosage
                            dispensed_qty += temp_qty
                        # dispenses = prescription.dispenses.filter(medicine__composition__name=composition.name).aggregate(
                        #     Sum('quantity'))
                        # if dispenses['quantity__sum']:
                        #     dispensed_qty = dispenses['quantity__sum']
                        dispensed_qty = int(dispensed_qty)
                        if required_qty != dispensed_qty:
                            dispense_flag = False
                    if dispense_flag:
                        prescription.dispensed = True
                        prescription.save()
            return Response({'status': "Success"})
        except Exception, e:
            return Response({'Error': e.message}, status=400)

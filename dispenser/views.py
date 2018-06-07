# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from dispenser.models import Device, Chamber, Load, LoadData
from dispenser.serializers import DeviceSerializer
from doctor.models import Medicine
from users.models import User
from django.shortcuts import render
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.http import HttpResponseRedirect
from .forms import PostForm

class VendorLoadAPI(APIView):
    def post(self, request):
        datas = request.data
        datas = json.loads(datas)
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

def Dev(request):
    dis=Device.objects.all()
    context={"dis":dis,}
    return render(request,'dispenser/dispenser.html',context)

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

import json

from dal import autocomplete
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import DispenseLog, Chamber, Device
from doctor.models import Composition, Prescription
from doctor.models import Schedule
from doctor.serializers import CompositionSerializer
from users.models import User
from users.serializers import UserSerializer, PrescriptionSerializer


class CompositionAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        query_set = Composition.objects.all()
        if self.q:
            query_set = Composition.objects.filter(name__icontains=self.q).order_by('name')
        return query_set


class CompositionList(APIView):
    def get(self, request):
        queryset = Composition.objects.all()
        serializer = CompositionSerializer(queryset, many=True)
        return Response(serializer.data)


class CompletePrescription(APIView):
    def post(self, request):
        data = request.POST
        doctor_id = data.get("doctor_id")
        items = data.get("items")
        patient_id = data.get("patient_id")
        description = data.get("description")
        prescription = Prescription.objects.create(patient_id=patient_id, doctor_id=doctor_id, doctor_note=description)
        items = json.loads(items)
        for item in items:
            nod = item.get("nod")
            for id, qty in enumerate(item.get('slots')):
                try:
                    if qty > 0:
                        schedule = Schedule()
                        schedule.prescription = prescription
                        schedule.composition_id = item.get("id")
                        schedule.slot = id
                        schedule.no_of_days = nod[id]
                        schedule.qty = qty
                        schedule.save()
                except Exception, e:
                    pass
        return Response({'status': 'success'}, status=200)


class UserPrescriptionAPI(APIView):
    def get(self, request):
        aadhar = request.GET.get('aadhar_number')
        try:
            user = User.objects.get(aadhar_number=aadhar)
            prescriptions = user.patient_prescriptions.all()
            return Response(PrescriptionSerializer(prescriptions, many=True).data)
        except Exception, e:
            return Response({'error': 'Aadhar Number Missing'})


class DispenseLogAPI(APIView):
    def get(self, request):
        data = request.GET.get("data", None)
        if data:
            data = json.loads(data)
            for item in data:
                chamber_id = data.get("chamber_id", None)
                chamber = Chamber.objects.get(id=chamber_id)
                medicine = chamber.medicine.composition
                qty = item.get("quantity")
                DispenseLog.objects.create(medicine=medicine, qty=qty)
            return Response("Success")
        return Response("Error Data Missing", status=400)


class UserDetailAPI(APIView):
    def get(self, request):
        data = request.GET.get("aadhar_number", None)
        if data:
            user = User.objects.get(aadhar_number=data)
            return Response(UserSerializer(user).data)
        else:
            return Response({'error': 'Missing Parameters'}, status=400)


class PrescriptionAPI(APIView):
    def get(self, request):
        id = request.GET.get("id")
        device_id = request.GET.get("device_id")
        device = Device.objects.get(id=device_id)
        prescription = Prescription.objects.get(id=id)
        compositions = prescription.schedules.values('composition').distinct()
        data = []
        for composition in compositions:
            composition = composition['composition']
            composition = Composition.objects.get(id=composition)
            load = \
                device.loads.filter(load_data__medicine__composition=composition).order_by('created_at').reverse()[0]
            chamb_number = load.load_data.get(medicine__composition=composition).chamber.chamber_number
            total = 0
            for schedule in prescription.schedules.filter(composition=composition):
                total += schedule.qty * schedule.no_of_days
            data.append({'name': composition.name, 'qty': total, 'chamber_number': chamb_number})
        return Response(data)

import json

from dal import autocomplete
from rest_framework.response import Response
from rest_framework.views import APIView

from doctor.models import Composition, Prescription
from doctor.models import Schedule
from doctor.serializers import CompositionSerializer


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
            for id, qty in enumerate(item.get('slots')):
                try:
                    if qty > 0:
                        schedule = Schedule()
                        schedule.prescription = prescription
                        schedule.composition_id = item.get("id")
                        schedule.slot = id
                        schedule.qty = qty
                        schedule.save()
                except Exception, e:
                    pass
        return Response({'status': 'success'}, status=200)

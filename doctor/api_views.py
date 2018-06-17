import json

from dal import autocomplete
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from dispenser.models import DispenseLog, Chamber, Device, Load, LoadData
from doctor.models import Composition, Prescription, Medicine
from doctor.models import Item
from doctor.serializers import CompositionSerializer, MedicineSerializer
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
                        schedule = Item()
                        schedule.prescription = prescription
                        schedule.composition_id = item.get("id")
                        schedule.slot = id
                        schedule.no_of_days = nod[id]
                        schedule.quantity = qty
                        schedule.save()
                except Exception, e:
                    pass
        return Response({'status': 'success'}, status=200)


class UserPrescriptionAPI(APIView):
    def get(self, request):
        aadhar = request.GET.get('aadhar_number')
        try:
            user = User.objects.get(aadhar_number=int(aadhar))
            prescriptions = user.patient_prescriptions.filter(dispensed=False)
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
        if prescription.dispensed:
            return Response({'status': "Prescription Already Dispensed"}, status=400)
        compositions = prescription.items.values('composition').distinct()
        data = []
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
                temp_qty = prescription.dispenses.filter(medicine__composition__dosage=dosage,
                                                         medicine__composition__name=composition.name).distinct().aggregate(
                    Sum("quantity"))['quantity__sum'] * temp_dosage
                dispensed_qty += temp_qty
            # dispenses = prescription.dispenses.filter(medicine__composition__name=composition.name).aggregate(
            #     Sum('quantity'))
            # if dispenses['quantity__sum']:
            #     dispensed_qty = dispenses['quantity__sum']
            loads = device.loads.filter(load_data__medicine__composition__name=composition.name, dispensed=False,
                                        load_data__expired=False).distinct()
            quota = int(required_qty - dispensed_qty)
            medicine_id = None
            medicine = None
            multiplier = 100
            is_available = False
            if loads.exists():
                max_dispensable_qty = 0
                dosages = loads.values('load_data__medicine__composition__dosage', 'load_data__medicine').distinct()
                denominations = {}
                dosage_medicine = None
                selected_available_qty = 0
                for dosage in dosages:
                    d = dosage
                    dosage = dosage['load_data__medicine__composition__dosage']
                    if composition.dosage % dosage == 0:
                        temp = composition.dosage / dosage
                        if temp < multiplier:
                            # Available Quantity Calculation
                            available_qty = 0
                            loadsd = LoadData.objects.filter(medicine__composition__dosage=dosage)
                            # loadsd = loads.filter(load_data__medicine__composition__dosage=dosage).distinct()
                            vacuum = False
                            for loadData in loadsd:
                                # loadsdd = load.load_data.filter(medicine__composition=composition,
                                #                                 medicine__composition__dosage=dosage).distinct()
                                # for loadData in loadsdd:
                                dispensed__qty = loadData.dispenses.all().aggregate(Sum('quantity'))[
                                    'quantity__sum']
                                if not dispensed__qty:
                                    dispensed__qty = 0
                                loaded_qty = loadData.quantity
                                if loadData.rate:
                                    loaded_qty = loadData.quantity * loadData.rate
                                    denominations[loadData.rate] = loaded_qty
                                qty = loaded_qty - dispensed__qty
                                if loadData.chamber.type == Chamber.VACUUM:
                                    if not vacuum:
                                        available_qty += (5 if qty > 5 else qty)
                                        vacuum = True
                                else:
                                    available_qty += qty
                            if required_qty <= available_qty:
                                selected_available_qty = available_qty
                                multiplier = temp
                                dosage_medicine_id = d['load_data__medicine']
                                dosage_medicine = Medicine.objects.get(id=dosage_medicine_id)
                is_available = True
                if multiplier != 1:
                    quota *= multiplier
                rem = quota
                for key, value in denominations.iteritems():
                    qt = denominations[key] / key
                    t = rem / key
                    if t < qt:
                        rem = 0
                        break
                    else:
                        rem -= denominations['key']
                if rem > 5:
                    is_available = False
                if selected_available_qty >= quota:
                    max_dispensable_qty = quota
                    medicine_id = dosage_medicine.id
                    medicine = dosage_medicine.__str__()
                data.append(
                    {'composition_name': composition.__str__(), 'composition_id': composition.id,
                     'prescribed_qty': required_qty, 'dispensed_qty': dispensed_qty,
                     'medicine_id': medicine_id, 'max_dispensable_qty': max_dispensable_qty, 'medicine': medicine,
                     'multiplier': multiplier, 'medicine_amount': dosage_medicine.price,
                     'is_available': is_available})
            else:
                data.append(
                    {'name': composition.__str__(), 'prescribed_qty': required_qty, 'multiplier': multiplier,
                     'dispensed_qty': dispensed_qty, 'is_available': False,
                     'medicine_id': medicine_id, 'medicine': medicine})
        loads = device.loads.filter(dispensed=False, load_data__expired=False).values('id').distinct()
        chamber_data = []
        medicines = loads.values('load_data__medicine').distinct()
        for load in loads:
            load_id = load['id']
            load = Load.objects.get(id=load_id)
            for load_data in load.load_data.all().order_by('-rate'):
                dict = {}
                dict['chamber_id'] = load_data.chamber.id
                dict['chamber'] = load_data.chamber.name
                dict['load_data'] = load_data.id
                dict['medicine_id'] = load_data.medicine.id
                dict['medicine'] = load_data.medicine.__str__()
                dict['composition'] = load_data.medicine.composition.__str__()
                dispensed_count = load_data.dispenses.all().aggregate(Sum('quantity'))['quantity__sum']
                if not dispensed_count:
                    dispensed_count = 0
                dict['rate'] = load_data.rate
                if load_data.rate:
                    dict['available_qty'] = (load_data.quantity * load_data.rate) - dispensed_count
                else:
                    dict['available_qty'] = load_data.quantity - dispensed_count
                chamber_data.append(dict)
        medicine_data = []
        for medicine in medicines:
            medicine_data.append(Medicine.objects.get(id=medicine['load_data__medicine']).__str__())
        finalized_data = {'prescription_data': data, 'chamber_data': chamber_data, 'medicines': medicine_data}
        return Response(finalized_data)


class MedicineListAPI(APIView):
    def get(self, request):
        medicines = Medicine.objects.all()
        return Response(MedicineSerializer(medicines, many=True).data)

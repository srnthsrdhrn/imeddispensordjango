from rest_framework import serializers

from doctor.models import Composition, Medicine


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = '__all__'


class MedicineSerializer(serializers.ModelSerializer):
    composition = CompositionSerializer()

    class Meta:
        model = Medicine
        fields = '__all__'

from rest_framework import serializers

from dispenser.models import Device, Chamber, DispenseLog
from users.serializers import UserSerializer


class ChamberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamber
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    chambers = ChamberSerializer(many=True)
    vendor = UserSerializer()

    class Meta:
        model = Device
        fields = '__all__'


class DispenseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispenseLog
        fields = '__all__'

    def create(self, validated_data):
        return DispenseLog.objects.create(**validated_data)

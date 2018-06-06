from rest_framework import serializers

from dispenser.models import Device, Chamber
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

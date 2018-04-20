from rest_framework import serializers

from doctor.models import Schedule, Prescription
from doctor.serializers import CompositionSerializer
from users.models import User


class ScheduleSerializer(serializers.ModelSerializer):
    composition = CompositionSerializer()

    class Meta:
        model = Schedule
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'id', 'email', 'aadhar_number', 'username', 'profile_pic')


class PrescriptionSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)
    doctor = UserSerializer()
    
    class Meta:
        model = Prescription
        fields = '__all__'

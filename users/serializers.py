from rest_framework import serializers

from doctor.models import Item, Prescription
from doctor.serializers import CompositionSerializer
from users.models import User


class ItemSerializer(serializers.ModelSerializer):
    composition = CompositionSerializer()

    class Meta:
        model = Item
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        return obj.get_wallet_balance()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'id', 'email', 'aadhar_number', 'username', 'profile_pic','balance')


class PrescriptionSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)
    doctor = UserSerializer()

    class Meta:
        model = Prescription
        fields = '__all__'

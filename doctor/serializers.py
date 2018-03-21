from rest_framework import serializers

from doctor.models import Composition


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ('id', 'name',)

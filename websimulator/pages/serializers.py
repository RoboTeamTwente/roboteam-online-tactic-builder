from .models import CustomNode
from rest_framework import serializers

class CustomNodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomNode
        fields = ('name', 'type')
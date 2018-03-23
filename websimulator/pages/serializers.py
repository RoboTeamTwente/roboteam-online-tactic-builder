from .models import custom_node
from rest_framework import serializers

class CustomNodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = custom_node
        fields = ('name', 'type')
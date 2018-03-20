from websimulator.pages.models import custom_node
from rest_framework import serializers

class custom_node_serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = custom_node
        fields = ('name', 'type')
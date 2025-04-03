from rest_framework import serializers
from lms.models import Module, Content, Course



class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order']
    



class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        extra_kwargs = {
            'order': {'required': False}  # Make order optional if you want
        }


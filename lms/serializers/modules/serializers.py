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



from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from lms.models import Content, Text, File, Image, Video, Module

class ContentTypeField(serializers.Field):
    """Custom field to handle content type model names"""
    def to_representation(self, value):
        return value.model

    def to_internal_value(self, data):
        try:
            return ContentType.objects.get(model=data.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Invalid content type: {data}")

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ['id', 'owner', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'owner', 'title', 'file', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'owner', 'title', 'file', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'owner', 'title', 'url', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ContentSerializer(serializers.ModelSerializer):
    content_type = ContentTypeField()
    text = TextSerializer(required=False)
    video = VideoSerializer(required=False)
    image = ImageSerializer(required=False)
    file = FileSerializer(required=False)
    
    class Meta:
        model = Content
        fields = [
            'id', 'module', 'content_type', 'order',
            'text', 'video', 'image', 'file',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure only one content type is provided"""
        content_type = data.get('content_type')
        content_fields = ['text', 'video', 'image', 'file']
        provided_fields = [field for field in content_fields if field in data]
        
        if len(provided_fields) != 1:
            raise serializers.ValidationError("Exactly one content type must be provided")
        
        if provided_fields[0] != content_type.model:
            raise serializers.ValidationError(
                f"Content type '{content_type.model}' doesn't match provided data field '{provided_fields[0]}'"
            )
            
        return data
    
    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        module = validated_data.pop('module')
        user = self.context['request'].user
        
        # Create the specific content item
        content_data = validated_data.pop(content_type.model)
        content_model = {
            'text': Text,
            'video': Video,
            'image': Image,
            'file': File
        }[content_type.model]
        
        content_item = content_model.objects.create(owner=user, **content_data)
        
        # Create the Content instance
        content = Content.objects.create(
            module=module,
            content_type=content_type,
            object_id=content_item.id,
            **validated_data
        )
        return content
    
    def to_representation(self, instance):
        """Custom representation to include the nested content"""
        representation = super().to_representation(instance)
        content_item = instance.item
        content_type = instance.content_type.model
        
        if content_type == 'text':
            representation['text'] = TextSerializer(content_item).data
        elif content_type == 'video':
            representation['video'] = VideoSerializer(content_item).data
        elif content_type == 'image':
            representation['image'] = ImageSerializer(content_item).data
        elif content_type == 'file':
            representation['file'] = FileSerializer(content_item).data
            
        return representation
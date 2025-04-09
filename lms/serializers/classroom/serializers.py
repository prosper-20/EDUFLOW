from rest_framework import serializers
from django.urls import reverse
from lms.models import Classroom
from django.core.exceptions import ValidationError

class CreateClassroomSerializer(serializers.ModelSerializer):
    classroom_link = serializers.SerializerMethodField("get_class_room_link", read_only=True)

    
    class Meta:
        model = Classroom
        fields = ["class_id", "name", "level_restriction", "accepted_levels", "classroom_link"]
        extra_kwargs = {
            "class_id": {"required": False},
            "accepted_levels": {"required": False}
        }

    def get_class_room_link(self, obj:Classroom):
        return f"http://127.0.0.1:8000/lms/classroom/{obj.class_id}/join/"



    def validate(self, data):
        level_restriction = data.get("level_restriction")
        accepted_levels = data.get("accepted_levels")

        if level_restriction != False and not accepted_levels:
            raise ValidationError({
                "accepted_values": ["This field is required."]
            })
        return data
    


class ClassroomSerializer(serializers.ModelSerializer):
    classroom_link = serializers.SerializerMethodField("get_class_room_link")
    accepted_levels = serializers.StringRelatedField()
    
    class Meta:
        model = Classroom
        fields = ["class_id", "name", "level_restriction", "accepted_levels", "classroom_link"]
        extra_kwargs = {
            "class_id": {"required": False},
            "accepted_levels": {"required": False}
        }

    def get_class_room_link(self, obj:Classroom):
        return f"http://127.0.0.1:8000/lms/classroom/{obj.class_id}/join/"


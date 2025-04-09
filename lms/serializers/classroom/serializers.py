from rest_framework import serializers
from lms.models import Classroom
from django.core.exceptions import ValidationError

class CreateClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["class_id", "name", "level_restriction", "accepted_levels"]
        extra_kwargs = {
            "class_id": {"required": False},
            "accepted_levels": {"required": False}
        }


    def validate(self, data):
        level_restriction = data.get("level_restriction")
        accepted_levels = data.get("accepted_levels")

        if level_restriction != False and not accepted_levels:
            raise ValidationError({
                "accepted_values": ["This field is required."]
            })
        return data

from rest_framework import serializers
from django.urls import reverse
from lms.models import Classroom, ClassroomAnnouncement
from django.core.exceptions import ValidationError
from accounts.serializers import UserDetailSerializer, UserProfileSerializer


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
    


class ClassroomDetailSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField("get_student_count")
    classroom_link = serializers.SerializerMethodField("get_class_room_link")
    accepted_levels = serializers.StringRelatedField(many=True)
    students = serializers.SerializerMethodField("students_data")
    
    class Meta:
        model = Classroom
        fields = ["class_id", "name", "slug", "accepted_levels", "classroom_link", "student_count", "students"]

    def get_class_room_link(self, obj:Classroom):
        return f"http://127.0.0.1:8000/lms/classroom/{obj.class_id}/join/"
    

    def get_student_count(self, obj:Classroom):
        return obj.students.count()
    
    def students_data(self, obj:Classroom):
        students = obj.students.all()
        return UserDetailSerializer(students, many=True).data
    


class CreateClassRoomAnnouncementSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ClassroomAnnouncement
        fields = ["content", "classroom", "file"]
        extra_kwargs = {
            "file": {"required": False}
        }


class StudentAnnouncementInboxSerializer(serializers.ModelSerializer):
    classroom_name = serializers.StringRelatedField(read_only=True)
    instructor = serializers.SerializerMethodField("get_instructor_name")
    
    
    class Meta:
        model = ClassroomAnnouncement
        fields = ["classroom", "classroom_name", "instructor", "content", "file", "created_at"]
        extra_kwargs = {
            "file": {"required": False}
        }

    
    def get_instructor_name(self, obj:ClassroomAnnouncement):
        return obj.classroom.owner.username

    

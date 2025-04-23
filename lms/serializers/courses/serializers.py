from rest_framework import serializers
from lms.models import Course, Faculty, Department, Enrollment


class CreateCourseSerializer(serializers.ModelSerializer):
    faculty = serializers.CharField(required=True, max_length=30)
    department = serializers.CharField(required=True, max_length=30)

    class Meta:
        model = Course
        fields = ("faculty", "department", "name", "code")

    def validate_faculty(self, value):
        try:
            faculty = Faculty.objects.get(name=value)
            return faculty
        except Faculty.DoesNotExist:
            raise serializers.ValidationError(
                {"Error": f"Faculty with name {value} doesn't exist"}
            )

    def validate_department(self, value):
        try:
            department = Department.objects.get(name=value)
            return department
        except Course.DoesNotExist:
            raise serializers.ValidationError(
                {"Error": f"Course with name {value} doesn't exist"}
            )


class CourseSerializer(serializers.ModelSerializer):
    faculty = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    enrollments = serializers.SerializerMethodField("get_enrollment_count")

    class Meta:
        model = Course
        fields = (
            "faculty",
            "department",
            "name",
            "code",
            "description",
            "enrollments",
            "created_at",
            "updated_at",
        )

    def get_enrollment_count(self, obj: Course):
        return obj.enrollments.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["enrollment_date", "completion_date"]

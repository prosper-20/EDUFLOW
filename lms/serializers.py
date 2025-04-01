from rest_framework import serializers
from .models import Course, Faculty, Department



class CreateCourseSerializer(serializers.ModelSerializer):
    faculty = serializers.CharField(required=True, max_length=30)
    department = serializers.CharField(required=True, max_length=30)
    class Meta:
        model = Course
        fields = ('faculty', 'department',  'name', 'code')


    def validate_faculty(self, value):
        try:
            faculty = Faculty.objects.get(name=value)
            return faculty
        except Faculty.DoesNotExist:
            raise serializers.ValidationError({"Error": f"Faculty with name {value} doesn't exist"})
        
    
    def validate_department(self, value):
        try:
            department = Department.objects.get(name=value)
            return department
        except Course.DoesNotExist:
            raise serializers.ValidationError({"Error": f"Course with name {value} doesn't exist"})
        
        
    
class CourseSerializer(serializers.ModelSerializer):
    faculty = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    class Meta:
        model = Course
        fields = ('faculty', 'department', 'name', 'code', "description", 'created_at', 'updated_at')



from rest_framework import serializers
from django.core.exceptions import ValidationError
from lms.models import Task, TaskSubmission

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_id', 'task_type', 'task', 'task_file', 'slug', 'due_date', 'submission_type', 'available_from', 'available_from']
        extra_kwargs = {
            'task_id': {'required': False}
        }

    
    def validate(self, data):
        task_type = data.get('task_type')
        task_file = data.get('task_file')
        
        # Check if task requires a file
        if task_type in ['assignment', 'quiz assignment'] and not task_file:
            raise ValidationError({
                'task_file': 'File upload is required for assignment and quiz assignment tasks'
            })
        
        
        # Additional validation if needed
        if task_file and task_type == 'question':
            raise ValidationError({
                'task_file': 'File upload is not allowed for question-type tasks'
            })
            
        return data



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_type', 'task',  'slug', 'due_date', 'total_points']


class TaskSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField("get_student_name", read_only=True)
    # task_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskSubmission
        fields = ['student', 'text_content', 'file_upload', 'url_submission']
        extra_kwargs = {
            'text_content': {'required': False},
            'file_upload': {'required': False},
            'url_submission': {'required': False}
            }
        
    def validate(self, data):
        task_type = self.context['task_type']
        file_upload = data.get('file_upload')
        
        # Check if task requires a file
        if task_type in ['assignment', 'quiz assignment'] and not file_upload:
            raise ValidationError({
                'file_upload': 'File upload is required for assignment and quiz assignment tasks'
            })
        
        
        # # Additional validation if needed
        # if task_file and task_type == 'question':
        #     raise ValidationError({
        #         'task_file': 'File upload is not allowed for question-type tasks'
        #     })
            
        return data



    def get_student_name(self, obj:TaskSubmission):
        return obj.student.username, obj.student.email


    def get_task_type(self, obj):
        # Get from context if available, otherwise from the task
        return self.context.get('task_type', obj.task.task_type)
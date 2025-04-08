from django.shortcuts import render, get_object_or_404
from lms.serializers.courses.serializers import CreateCourseSerializer, CourseSerializer, EnrollmentSerializer
from lms.serializers.modules.serializers import ModuleCreateSerializer, ModuleSerializer, ContentSerializer, TaskCreateSerializer, TaskSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment, Module, Content, Task
from rest_framework.permissions import IsAuthenticated
from Generic.lms.permissions import IsCourseOwnerOrReadOnly, IsStudent, IsInstructor
from django.db.models import Count, Avg


class CreateCourseAPIView(APIView):
    permission_classes = [IsInstructor]

    def post(self, request):
        course = Course(owner=request.user)
        serializer = CreateCourseSerializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Course Creation Successful!",
                         "data": serializer.data}, status=status.HTTP_201_CREATED)
    


class RetrieveCourseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCourseOwnerOrReadOnly]  


    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Course Updated Successfully!",
                         "data": serializer.data}, status=status.HTTP_200_OK)
    

    def delete(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course.delete()
        return Response({"Success": "Course Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)
    


# class CreateEnrollmentAPIView(APIView):
#     permission_classes = [IsStudent]

#     def post(self, request, slug):
#         student = request.user
#         course = get_object_or_404(Course, slug=slug)
#         enrollemnt = Enrollment.objects.filter(course=course, student=student)
#         if enrollemnt.exists():
#             return Response({"Error": "You are already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             enrollment = Enrollment.objects.create(student=student, course=course)
#             serializer = EnrollmentSerializer(enrollemnt)
#         return Response({"Success": "You have successfully enrolled!",
#                          "data": serializer.data}, status=status.HTTP_201_CREATED)


    
    
class CreateEnrollmentAPIView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, slug):
        student = request.user
        course = get_object_or_404(Course, slug=slug)
        existing_enrollment = Enrollment.objects.filter(course=course, student=student)
        
        if existing_enrollment.exists():
            return Response(
                {"Error": "You are already enrolled in this course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = Enrollment.objects.create(student=student, course=course)
        serializer = EnrollmentSerializer(enrollment)
        
        return Response({"Success": "You have successfully enrolled!", "data": serializer.data}, status=status.HTTP_201_CREATED)
    


class ListAllMyCourseEnrollments(APIView):
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        completed = self.request.query_params.get('completed')
        data = {}
        student = request.user
        if completed:
           enrollments = Enrollment.objects.filter(student=student, status='completed')
        else:
            enrollments = Enrollment.objects.filter(student=student)
        enrollment_count = enrollments.count()
        data["enrollment_count"] = enrollment_count
        serializer = EnrollmentSerializer(enrollments, many=True)
        data.update({"data": serializer.data})
        return Response(data, status=status.HTTP_200_OK)



class CreateModuleAPIView(APIView):
    permission_classes = [IsInstructor]

    def post(self, request, slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=slug)
        module = Module(course=course)
        serializer = ModuleCreateSerializer(module, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Module created successfully",
                         "data": serializer.data}, status=status.HTTP_201_CREATED)


class ListCourseModuleAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]  # Any authenticated user can view
        elif self.request.method == 'PUT':
            return [IsInstructor()]  # Only instructors can create
        return super().get_permissions()


    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course_modules = course.modules.all()
        serializer = ModuleSerializer(course_modules, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    

class RetrieveCourseModuleAPIView(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

    def get(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        serializer = ModuleSerializer(module)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        serializer = ModuleCreateSerializer(module, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Module updated successfully!",
                         "data": serializer.data}, status=status.HTTP_200_OK)
    

    def delete(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        module.delete()
        return Response({"Success": "Module deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)



class ContentCreateAPIView(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

    def post(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        
        # Add module to request data
        request_data = request.data.copy()
        request_data['module'] = module.id
        
        serializer = ContentSerializer(data=request_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateTask(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

    def post(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        
        # Initialize serializer with all data including file
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create task with all validated data
        task = serializer.save(
            course=course,
            module=module,
            instructor=request.user
        )
        
        return Response({
            "Success": "Task creation successful!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    


class RetrieveTaskAPIView(APIView):
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsCourseOwnerOrReadOnly()]  # Any authenticated user can view
        elif self.request.method in ['PUT', 'DELETE']:
            return [IsInstructor()]  # Only instructors can create
        return super().get_permissions()

    def get(self, request, slug, module_id, task_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        task = get_object_or_404(Task, task_id=task_id, course=course, module=module)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, slug, module_id, task_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        task = get_object_or_404(Task, task_id=task_id, course=course, module=module)
    
        serializer = TaskCreateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Task update successful!",
                         "data":serializer.data}, status=status.HTTP_200_OK)
    

    def delete(self, request, slug, module_id, task_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        task = get_object_or_404(Task, task_id=task_id, course=course, module=module)
        task.delete()
        return Response({"Success": "Task deletion successful!"}, status=status.HTTP_204_NO_CONTENT)


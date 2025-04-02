from django.shortcuts import render, get_object_or_404
from .serializers import CreateCourseSerializer, CourseSerializer, EnrollmentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment
from rest_framework.permissions import IsAuthenticated
from Generic.lms.permissions import IsCourseOwnerOrReadOnly, IsStudent

class CreateCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
        
        # Check for existing enrollment (fixed typo in variable name)
        existing_enrollment = Enrollment.objects.filter(course=course, student=student)
        
        if existing_enrollment.exists():
            return Response(
                {"Error": "You are already enrolled in this course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new enrollment
        enrollment = Enrollment.objects.create(student=student, course=course)
        
        # Serialize the created enrollment instance (not the queryset)
        serializer = EnrollmentSerializer(enrollment)
        
        return Response(
            {
                "Success": "You have successfully enrolled!",
                "data": serializer.data
            }, 
            status=status.HTTP_201_CREATED
        )


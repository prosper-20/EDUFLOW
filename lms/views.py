from django.shortcuts import render, get_object_or_404
from .serializers import CreateCourseSerializer, CourseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course
from rest_framework.permissions import IsAuthenticated
from Generic.lms.permissions import IsCourseOwnerOrReadOnly

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
    
    



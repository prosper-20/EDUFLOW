from asyncio.log import logger
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from Generic.utils import is_valid_file_type
from lms.serializers.courses.serializers import (
    CreateCourseSerializer,
    CourseSerializer,
    EnrollmentSerializer,
)
from lms.serializers.modules.serializers import (
    ModuleCreateSerializer,
    ModuleSerializer,
    ContentSerializer,
)
from lms.serializers.tasks.serializers import (
    TaskCreateSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
    TaskSubmissionDetailSerializer,
    GradeTaskSubmissionSerializer,
    RetrieveTaskSubmissionGradeSerializer,
)
from lms.serializers.classroom.serializers import (
    CreateClassroomSerializer,
    ClassroomSerializer,
    ClassroomDetailSerializer,
    CreateClassRoomAnnouncementSerializer,
    StudentAnnouncementInboxSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Classroom,
    Course,
    Enrollment,
    Module,
    Content,
    Task,
    TaskSubmission,
    ClassroomAnnouncement,
)
from rest_framework.permissions import IsAuthenticated
from Generic.lms.permissions import IsCourseOwnerOrReadOnly, IsStudent, IsInstructor
from django.db.models import Count, Avg
from exceptions.custom_exceptions import *
from django.core.exceptions import ValidationError


class CreateCourseAPIView(APIView):
    permission_classes = [IsInstructor]

    def post(self, request):
        course = Course(owner=request.user)
        serializer = CreateCourseSerializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"Success": "Course Creation Successful!", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


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
        return Response(
            {"Success": "Course Updated Successfully!", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course.delete()
        return Response(
            {"Success": "Course Deleted Successfully!"},
            status=status.HTTP_204_NO_CONTENT,
        )


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
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = Enrollment.objects.create(student=student, course=course)
        serializer = EnrollmentSerializer(enrollment)

        return Response(
            {"Success": "You have successfully enrolled!", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ListAllMyCourseEnrollments(APIView):
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        completed = self.request.query_params.get("completed")
        data = {}
        student = request.user
        if completed:
            enrollments = Enrollment.objects.filter(student=student, status="completed")
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
        return Response(
            {"Success": "Module created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ListCourseModuleAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]  # Any authenticated user can view
        elif self.request.method == "PUT":
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
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        serializer = ModuleCreateSerializer(module, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"Success": "Module updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        module.delete()
        return Response(
            {"Success": "Module deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT,
        )


class ContentCreateAPIView(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

    def post(self, request, slug, module_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)

        # Add module to request data
        request_data = request.data.copy()
        request_data["module"] = module.id

        serializer = ContentSerializer(data=request_data, context={"request": request})
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
        task = serializer.save(course=course, module=module, instructor=request.user)

        return Response(
            {"Success": "Task creation successful!", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CreateTaskSubmission(APIView):
    permission_classes = [IsStudent]

    def post(self, request, task_id):
        try:
            task = get_object_or_404(Task, task_id=task_id)

            # Check for existing submission
            if TaskSubmission.objects.filter(task=task, student=request.user).exists():
                raise DuplicateSubmissionError()

            # Handle file submission validation
            if task.submission_type == "file":
                file = request.FILES.get("file_upload")

                if not file:
                    raise ValidationError("No file was uploaded")

                if not is_valid_file_type(file, task.allowed_file_types.all()):
                    allowed_extensions = list(
                        task.allowed_file_types.values_list("ext", flat=True)
                    )
                    raise InvalidFileTypeError(
                        detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
                    )

                # Check file size (in MB)
                max_size = task.max_file_size * 1024 * 1024  # Convert MB to bytes
                if file.size > max_size:
                    raise FileSizeExceededError(
                        detail=f"File size exceeds maximum allowed size of {task.max_file_size}MB"
                    )

            # Create the submission
            task_submission = TaskSubmission(student=request.user, task=task)
            serializer = TaskSubmissionSerializer(
                task_submission,
                data=request.data,
                context={"task_type": task.task_type},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"success": "Submission saved successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            raise  # This will be caught by your custom exception handler


# class RetrieveTaskSubmissionsAPIView(APIView):
#     permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

#     def get(self, request, task_id, *args, **kwargs):
#         is_graded = request.query_params.get("is_graded")
#         is_not_graded = request.query_params.get("is_not_graded")

#         if is_graded:
#             task_submissions = TaskSubmission.objects.filter(task=task_id, is_graded=True)
#         elif is_not_graded:
#             task_submissions = TaskSubmission.objects.filter(task=task_id, is_graded=False)
#         else:
#             task_submissions = TaskSubmission.objects.filter(task__task_id=task_id)
#             serializer =TaskSubmissionDetailSerializer(task_submissions, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveTaskSubmissionsAPIView(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]
    serializer_class = (
        TaskSubmissionDetailSerializer  # Define serializer at class level
    )

    def get_queryset(self, task_id):
        queryset = TaskSubmission.objects.filter(task__task_id=task_id)
        is_graded = self.request.query_params.get("is_graded")
        if is_graded is not None:
            queryset = queryset.filter(is_graded=str(is_graded).lower() == "true")
        return queryset

    def get(self, request, task_id, *args, **kwargs):
        try:
            task_submissions = self.get_queryset(task_id)

            # Use select_related/prefetch_related to optimize DB queries
            task_submissions = task_submissions.select_related(
                "student", "task", "task__course"
            )

            serializer = self.serializer_class(task_submissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving task submissions: {str(e)}")
            return Response(
                {"error": "Failed to retrieve task submissions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GradeTaskSubmissionAPIView(APIView):
    permission_class = [IsInstructor, IsCourseOwnerOrReadOnly]

    def post(self, request, task_id, submission_id):
        task_submission = get_object_or_404(
            TaskSubmission, task__task_id=task_id, submission_id=submission_id
        )
        serializer = GradeTaskSubmissionSerializer(task_submission, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            graded_by=self.request.user, graded_at=datetime.now(), is_graded=True
        )
        serializer = TaskSubmissionDetailSerializer(task_submission)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveGradesTaskSubmissionAPIView(APIView):
    permission_class = [IsInstructor, IsCourseOwnerOrReadOnly]

    def get(self, request, task_id):
        all_submissions = TaskSubmission.objects.filter(task__task_id=task_id).order_by(
            "grade"
        )
        graded_submissions = all_submissions.filter(is_graded=True)
        serializer = RetrieveTaskSubmissionGradeSerializer(all_submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveTaskAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsCourseOwnerOrReadOnly()]  # Any authenticated user can view
        elif self.request.method in ["PUT", "DELETE"]:
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
        return Response(
            {"Success": "Task update successful!", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, slug, module_id, task_id):
        course = get_object_or_404(Course, slug=slug)
        module = get_object_or_404(Module, id=module_id, course=course)
        task = get_object_or_404(Task, task_id=task_id, course=course, module=module)
        task.delete()
        return Response(
            {"Success": "Task deletion successful!"}, status=status.HTTP_204_NO_CONTENT
        )


class CreateClassromAPIView(APIView):
    permission_classes = [IsInstructor]

    def post(self, request):
        user = request.user
        classroom = Classroom(owner=user)
        serializer = CreateClassroomSerializer(classroom, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"Success": "Classroom created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CreateClassroomAnnouncementAPIView(APIView):
    permission_classes = [IsInstructor, IsCourseOwnerOrReadOnly]

    def post(self, request, class_id):
        classroom = get_object_or_404(Classroom, class_id=class_id)
        announcement = ClassroomAnnouncement(classroom=classroom)
        serializer = CreateClassRoomAnnouncementSerializer(
            announcement, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "Success": "Classroom announcement created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class MyClassroomAnnouncementAPIView(APIView):
    """
    Retrieves all announcements from all the
    classes a student is registered in.
    """

    permission_classes = [IsStudent]

    def get(self, request):
        student = request.user
        announcements = ClassroomAnnouncement.objects.filter(
            classroom__students=student
        ).order_by("-created_at")

        serializer = StudentAnnouncementInboxSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveClassroomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        classroom = get_object_or_404(Classroom, class_id=class_id)
        serializer = ClassroomSerializer(classroom)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveClassroomMetaDataAPIView(APIView):
    permission_classes = [IsInstructor]

    def get(self, request, class_id):
        classroom = get_object_or_404(Classroom, class_id=class_id)
        serializer = ClassroomDetailSerializer(classroom)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentJoinClassroomAPIView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, class_id):
        user = request.user
        classroom = get_object_or_404(Classroom, class_id=class_id)

        if classroom.students.filter(id=user.id).exists():
            return Response(
                {"error": "Student is already in this classroom"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check level restriction if enabled
        if classroom.level_restriction:
            student_level = user.userprofile.level  # Assuming user has a 'level' field
            if not classroom.accepted_levels.filter(id=student_level.id).exists():
                return Response(
                    {"error": "Student's level is not accepted in this classroom"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        classroom.students.add(user)
        return Response(
            {"Success": "Student joined the classroom successfully"},
            status=status.HTTP_200_OK,
        )

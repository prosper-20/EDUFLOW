from django.urls import path
from .views import CreateCourseAPIView, RetrieveCourseAPIView, CreateEnrollmentAPIView, ListAllMyCourseEnrollments, CreateModuleAPIView, ListCourseModuleAPIView, RetrieveCourseModuleAPIView, ContentCreateAPIView, CreateTask, RetrieveTaskAPIView, CreateClassromAPIView, StudentJoinClassroomAPIView, RetrieveClassroomAPIView, CreateTaskSubmission, RetrieveTaskSubmissionsAPIView, GradeTaskSubmissionAPIView

CLASSROOM_URLS = [
    path("classroom/create/", CreateClassromAPIView.as_view(), name="create-classroom"),
    path("classroom/<str:class_id>/", RetrieveClassroomAPIView.as_view(), name="retrieve-classroom"),
    path("classroom/<str:class_id>/join/", StudentJoinClassroomAPIView.as_view(), name="join-class"),

]


TASK_URLS = [
    path('courses/<str:slug>/<int:module_id>/create/task/', CreateTask.as_view(), name='task-create'),
    path("courses/<str:slug>/<int:module_id>/tasks/<uuid:task_id>/", RetrieveTaskAPIView.as_view(), name="retrieve-task"),
    
]

TASK_SUBMISSION_URLS = [
    path("courses/task/<uuid:task_id>/", CreateTaskSubmission.as_view(), name="create-task-submission"),
    path("courses/task/<uuid:task_id>/submissions/", RetrieveTaskSubmissionsAPIView.as_view(), name="retrieve-task-submisions"),
    path("courses/task/<uuid:task_id>/submissions/<uuid:submission_id>/grade/", GradeTaskSubmissionAPIView.as_view(), name="grade-task-submision"),


]

urlpatterns = [
    path("courses/create/", CreateCourseAPIView.as_view(), name="create-course"),
    path("courses/my-enrollments/", ListAllMyCourseEnrollments.as_view(), name="list-course-enrollments"),
    path("courses/<str:slug>/", RetrieveCourseAPIView.as_view(), name="retrieve-course"),
    path("courses/<str:slug>/enroll/", CreateEnrollmentAPIView.as_view(), name="create-course-enrollment"),
    path("courses/<str:slug>/create/module/", CreateModuleAPIView.as_view(), name="create-course-module"),
    path("courses/<str:slug>/modules/", ListCourseModuleAPIView.as_view(), name="list-course-modules"),
    path("courses/<str:slug>/<int:module_id>/", RetrieveCourseModuleAPIView.as_view(), name="retrieve"),
    path("courses/<str:slug>/<int:module_id>/create/content/", ContentCreateAPIView.as_view(), name="create-course-content"),
    *TASK_URLS,
    *CLASSROOM_URLS,
    *TASK_SUBMISSION_URLS
    ] 

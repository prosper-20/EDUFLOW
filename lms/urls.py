from django.urls import path
from .views import CreateCourseAPIView, RetrieveCourseAPIView, CreateEnrollmentAPIView, ListAllMyCourseEnrollments, CreateModuleAPIView, ListCourseModuleAPIView, RetrieveCourseModuleAPIView, ContentCreateAPIView, CreateTask, RetrieveTaskAPIView


TASK_URLS = [
    path('courses/<str:slug>/<int:module_id>/create/task/', CreateTask.as_view(), name='task-create'),
    path("courses/<str:slug>/<int:module_id>/tasks/<uuid:task_id>/", RetrieveTaskAPIView.as_view(), name="retrieve-task")
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
    *TASK_URLS
    ] 

from django.urls import path, include
from .views import (
    CreateCourseAPIView,
    AddCourseToFavouriteAPIView,
    RetrieveCourseAPIView,
    CreateEnrollmentAPIView,
    ListAllMyCourseEnrollments,
    CreateModuleAPIView,
    ListCourseModuleAPIView,
    RetrieveCourseModuleAPIView,
    ContentCreateAPIView,
    CreateTask,
    RetrieveTaskAPIView,
    CreateClassromAPIView,
    StudentJoinClassroomAPIView,
    RetrieveClassroomAPIView,
    CreateTaskSubmission,
    RetrieveTaskSubmissionsAPIView,
    GradeTaskSubmissionAPIView,
    RetrieveClassroomMetaDataAPIView,
    RetrieveGradesTaskSubmissionAPIView,
    CreateClassroomAnnouncementAPIView,
    MyClassroomAnnouncementAPIView,
    CommentListCreateView,
    ContentRetrieveAPIView,
    CommentReplyView,
    CommentRetrieveUpdateDestroyView,
    CommentDeactivateAPIView,
)
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, OptionViewSet, QuizViewSet, QuizQuestionViewSet

router = DefaultRouter()
router.register('questions', QuestionViewSet)
router.register('options', OptionViewSet)
router.register('quiz', QuizViewSet)
router.register('my-quiz-questions', QuizQuestionViewSet)


    

CLASSROOM_URLS = [
    path("classroom/create/", CreateClassromAPIView.as_view(), name="create-classroom"),
    path(
        "classroom/announcements/",
        MyClassroomAnnouncementAPIView.as_view(),
        name="classroom-announcements",
    ),
    path(
        "classroom/<str:class_id>/",
        RetrieveClassroomAPIView.as_view(),
        name="retrieve-classroom",
    ),
    path(
        "classroom/<str:class_id>/create/",
        CreateClassroomAnnouncementAPIView.as_view(),
        name="create-classroom-announcement",
    ),
    path(
        "classroom/<str:class_id>/metadata/",
        RetrieveClassroomMetaDataAPIView.as_view(),
        name="retrieve-classroom-metadata",
    ),
    path(
        "classroom/<str:class_id>/join/",
        StudentJoinClassroomAPIView.as_view(),
        name="join-class",
    ),
]


TASK_URLS = [
    path(
        "courses/<str:slug>/<int:module_id>/create/task/",
        CreateTask.as_view(),
        name="task-create",
    ),
    path(
        "courses/<str:slug>/<int:module_id>/tasks/<uuid:task_id>/",
        RetrieveTaskAPIView.as_view(),
        name="retrieve-task",
    ),
]

TASK_SUBMISSION_URLS = [
    path(
        "courses/task/<uuid:task_id>/",
        CreateTaskSubmission.as_view(),
        name="create-task-submission",
    ),
    path(
        "courses/task/<uuid:task_id>/submissions/",
        RetrieveTaskSubmissionsAPIView.as_view(),
        name="retrieve-task-submisions",
    ),
    path(
        "courses/task/<uuid:task_id>/submissions/scores/",
        RetrieveGradesTaskSubmissionAPIView.as_view(),
        name="retrieve-submissions-scores",
    ),
    path(
        "courses/task/<uuid:task_id>/submissions/<uuid:submission_id>/grade/",
        GradeTaskSubmissionAPIView.as_view(),
        name="grade-task-submision",
    ),
]

COMMENT_URLS = [
    path(
        "comments/<int:pk>/replies/", CommentReplyView.as_view(), name="comment-replies"
    ),
    path(
        "comments/<int:pk>/",
        CommentRetrieveUpdateDestroyView.as_view(),
        name="comment-detail",
    ),
    path(
        "contents/<uuid:content_id>/comments/",
        CommentListCreateView.as_view(),
        name="content-comments",
    ),
    path(
        'comments/<int:pk>/deactivate/',
        CommentDeactivateAPIView.as_view(),
        name='comment-deactivate'
    ),
]

QUIZ_URLS = [
    path('', include(router.urls)),
]

urlpatterns = [
    path("courses/create/", CreateCourseAPIView.as_view(), name="create-course"),
    path(
        "courses/my-enrollments/",
        ListAllMyCourseEnrollments.as_view(),
        name="list-course-enrollments",
    ),
    path(
        "courses/content/<uuid:content_id>/",
        ContentRetrieveAPIView.as_view(),
        name="retrieve-course-content",
    ),
    path(
        "courses/<str:slug>/", RetrieveCourseAPIView.as_view(), name="retrieve-course"
    ),
    path(
        "courses/<str:slug>/enroll/",
        CreateEnrollmentAPIView.as_view(),
        name="create-course-enrollment",
    ),
    path(
        "courses/<str:slug>/create/module/",
        CreateModuleAPIView.as_view(),
        name="create-course-module",
    ),
    path(
        "courses/<str:slug>/modules/",
        ListCourseModuleAPIView.as_view(),
        name="list-course-modules",
    ),
    path(
        "courses/<str:slug>/<int:module_id>/",
        RetrieveCourseModuleAPIView.as_view(),
        name="retrieve",
    ),
    path(
        "courses/<str:slug>/<int:module_id>/create/content/",
        ContentCreateAPIView.as_view(),
        name="create-course-content",
    ),
    path(
        "courses/<str:slug>/favourites/",
        AddCourseToFavouriteAPIView.as_view(),
        name="add-course-to-favourites",
    ),
    *TASK_URLS,
    *CLASSROOM_URLS,
    *TASK_SUBMISSION_URLS,
    *COMMENT_URLS,
    *QUIZ_URLS
]

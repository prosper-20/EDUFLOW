from rest_framework.exceptions import APIException
from rest_framework import status

class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, status_code):
        super().__init__(detail, status_code)
        self.detail = detail
        self.status_code = status_code

class DuplicateSubmissionError(BaseCustomException):
    def __init__(self, detail="You have already submitted this task"):
        super().__init__(detail, status.HTTP_409_CONFLICT)

class InvalidFileTypeError(BaseCustomException):
    def __init__(self, detail="Invalid file type submitted"):
        super().__init__(detail, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

class FileSizeExceededError(BaseCustomException):
    def __init__(self, detail="File size exceeds the maximum allowed"):
        super().__init__(detail, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

class ResourceNotFoundError(BaseCustomException):
    def __init__(self, detail="Requested resource not found"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)
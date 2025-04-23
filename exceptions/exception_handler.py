from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import traceback
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Handle Django's IntegrityError (database errors)
    if isinstance(exc, IntegrityError):
        logger.error(f"IntegrityError: {str(exc)}")
        logger.error(traceback.format_exc())

        # Handle duplicate submission case
        if (
            "unique constraint" in str(exc).lower()
            and "tasksubmission" in str(exc).lower()
        ):
            return Response(
                {"error": "You have already submitted this task"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"error": "A database integrity error occurred. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle Django's ValidationError
    elif isinstance(exc, ValidationError):
        logger.error(f"ValidationError: {str(exc)}")
        return Response(
            {"error": "Validation error", "details": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle Python's built-in exceptions
    elif isinstance(exc, (ValueError, TypeError)):
        logger.error(f"{type(exc).__name__}: {str(exc)}")
        return Response(
            {"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Handle AttributeError
    elif isinstance(exc, AttributeError):
        logger.error(f"AttributeError: {str(exc)}")
        return Response(
            {"error": "An attribute error occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Handle KeyError
    elif isinstance(exc, KeyError):
        logger.error(f"KeyError: {str(exc)}")
        return Response(
            {"error": f"Missing required field: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle other uncaught exceptions
    elif response is None:
        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(traceback.format_exc())
        return Response(
            {"error": "An unexpected error occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response

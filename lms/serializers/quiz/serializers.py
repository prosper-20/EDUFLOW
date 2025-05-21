from rest_framework import serializers
from lms.models import Course, Question, Option, Quiz, QuizQuestion


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["question", "text", "text_words", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "course",
            "text",
            "marks",
            "options",
            "created_at",
            "updated_at",
        ]


class QuizQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ["id", "quiz", "question", "order"]


class QuizSerializer(serializers.ModelSerializer):
    quiz_questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "course",
            "title",
            "slug",
            "description",
            "duration",
            "is_active",
            "quiz_questions",
            "created_at",
            "updated_at",
        ]

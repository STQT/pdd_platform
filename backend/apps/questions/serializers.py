from rest_framework import serializers
from .models import Category, Question, Answer


class CategorySerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title_ru", "title_kz", "order", "question_count"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "original_id", "text_ru", "text_kz", "text_en", "order", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    category_title = serializers.CharField(source="category.title_ru", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "original_id", "category_id", "category_title",
            "text_ru", "text_kz", "text_en",
            "question_media",
            "explanation_ru", "explanation_kz", "explanation_en",
            "explanation_media", "explanation2_media",
            "correct_answer_index", "answers",
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists — no answers, no correct answer."""
    category_id = serializers.IntegerField(source="category.id", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "original_id", "category_id", "text_ru", "text_kz", "question_media"]

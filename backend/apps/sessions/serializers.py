from rest_framework import serializers
from apps.questions.serializers import QuestionSerializer
from apps.questions.models import Question
from .models import TestSession, SessionAnswer


class StartSessionSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(required=False, allow_null=True)
    mode = serializers.ChoiceField(choices=["training", "exam"], default="training")


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()


class SessionAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id")
    answer_id = serializers.IntegerField(source="chosen_answer.id")

    class Meta:
        model = SessionAnswer
        fields = ["question_id", "answer_id", "is_correct", "answered_at"]


class TestSessionSerializer(serializers.ModelSerializer):
    current_question = serializers.SerializerMethodField()
    total = serializers.IntegerField(read_only=True)
    answered = serializers.IntegerField(read_only=True)

    class Meta:
        model = TestSession
        fields = [
            "session_key", "category_id", "mode", "status",
            "current_index", "correct_count", "wrong_count",
            "total", "answered", "current_question",
            "created_at", "finished_at",
        ]

    def get_current_question(self, obj):
        if obj.status != TestSession.STATUS_ACTIVE:
            return None
        if obj.current_index >= len(obj.question_ids):
            return None
        q_pk = obj.question_ids[obj.current_index]
        try:
            q = Question.objects.prefetch_related("answers").get(pk=q_pk)
            return QuestionSerializer(q).data
        except Question.DoesNotExist:
            return None


class ResultsSerializer(serializers.ModelSerializer):
    answers = SessionAnswerSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)
    answered = serializers.IntegerField(read_only=True)
    pass_rate = serializers.SerializerMethodField()

    class Meta:
        model = TestSession
        fields = [
            "session_key", "category_id", "mode", "status",
            "correct_count", "wrong_count", "total", "answered",
            "pass_rate", "answers", "created_at", "finished_at",
        ]

    def get_pass_rate(self, obj):
        if not obj.total:
            return 0
        return round(obj.correct_count / obj.total * 100, 1)

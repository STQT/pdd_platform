import random
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.questions.models import Question
from .models import TestSession, SessionAnswer
from .serializers import (
    StartSessionSerializer,
    SubmitAnswerSerializer,
    TestSessionSerializer,
    ResultsSerializer,
)

EXAM_QUESTION_COUNT = 20
EXAM_MAX_WRONG = 3


class StartSessionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StartSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_id = data.get("category_id")
        mode = data["mode"]

        qs = Question.objects.all()
        if category_id:
            qs = qs.filter(category_id=category_id)

        question_pks = list(qs.values_list("id", flat=True))
        if not question_pks:
            return Response({"detail": "No questions found."}, status=400)

        if mode == TestSession.MODE_EXAM:
            count = min(EXAM_QUESTION_COUNT, len(question_pks))
            question_pks = random.sample(question_pks, count)
        else:
            random.shuffle(question_pks)

        session = TestSession.objects.create(
            category_id=category_id,
            mode=mode,
            question_ids=question_pks,
        )
        return Response(TestSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class SessionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_key):
        try:
            session = TestSession.objects.get(session_key=session_key)
        except TestSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(TestSessionSerializer(session).data)


class SubmitAnswerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, session_key):
        try:
            session = TestSession.objects.get(session_key=session_key)
        except TestSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        if session.status != TestSession.STATUS_ACTIVE:
            return Response({"detail": "Session already finished."}, status=400)

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            question = Question.objects.prefetch_related("answers").get(pk=data["question_id"])
        except Question.DoesNotExist:
            return Response({"detail": "Question not found."}, status=404)

        try:
            answer = question.answers.get(pk=data["answer_id"])
        except Exception:
            return Response({"detail": "Answer not found."}, status=404)

        # Prevent double-answering
        if session.answers.filter(question=question).exists():
            return Response({"detail": "Already answered."}, status=400)

        is_correct = answer.is_correct
        SessionAnswer.objects.create(
            session=session,
            question=question,
            chosen_answer=answer,
            is_correct=is_correct,
        )

        if is_correct:
            session.correct_count += 1
        else:
            session.wrong_count += 1

        session.current_index += 1

        # Finish conditions
        finished = False
        if session.current_index >= session.total:
            finished = True
        elif session.mode == TestSession.MODE_EXAM and session.wrong_count >= EXAM_MAX_WRONG:
            finished = True

        if finished:
            session.status = (
                TestSession.STATUS_PASSED
                if session.wrong_count < EXAM_MAX_WRONG
                else TestSession.STATUS_FAILED
            )
            session.finished_at = timezone.now()

        session.save()

        response_data = {
            "is_correct": is_correct,
            "correct_answer_id": question.answers.filter(is_correct=True).values_list("id", flat=True).first(),
            "session": TestSessionSerializer(session).data,
        }

        # In training mode, always show explanation
        if session.mode == TestSession.MODE_TRAINING:
            response_data["explanation_media"] = question.explanation_media

        return Response(response_data)


class SessionResultsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_key):
        try:
            session = TestSession.objects.prefetch_related(
                "answers__question", "answers__chosen_answer"
            ).get(session_key=session_key)
        except TestSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        return Response(ResultsSerializer(session).data)

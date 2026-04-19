from django.db.models import Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Question
from .serializers import CategorySerializer, QuestionSerializer, QuestionListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(question_count=Count("questions")).order_by("order")

    @action(detail=True, methods=["get"], url_path="questions")
    def questions(self, request, pk=None):
        category = self.get_object()
        qs = category.questions.prefetch_related("answers").order_by("id")
        serializer = QuestionSerializer(qs, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Question.objects.prefetch_related("answers").select_related("category")
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return QuestionListSerializer
        return QuestionSerializer

from django.contrib import admin
from .models import Category, Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title_ru", "order"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "original_id", "category", "text_ru"]
    list_filter = ["category"]
    search_fields = ["text_ru", "original_id"]
    inlines = [AnswerInline]

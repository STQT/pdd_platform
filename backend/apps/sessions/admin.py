from django.contrib import admin
from .models import TestSession, SessionAnswer


class SessionAnswerInline(admin.TabularInline):
    model = SessionAnswer
    extra = 0
    readonly_fields = ["question", "chosen_answer", "is_correct", "answered_at"]


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "category", "mode", "status", "correct_count", "wrong_count", "created_at"]
    list_filter = ["mode", "status", "category"]
    readonly_fields = ["session_key", "created_at", "finished_at"]
    inlines = [SessionAnswerInline]

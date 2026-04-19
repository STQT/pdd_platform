from django.contrib import admin
from .models import TestSession, SessionAnswer, TelegramUser


class SessionAnswerInline(admin.TabularInline):
    model = SessionAnswer
    extra = 0
    readonly_fields = ["question", "chosen_answer", "is_correct", "answered_at"]


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "first_name", "username", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["chat_id", "username", "first_name", "last_name"]
    readonly_fields = ["chat_id", "created_at", "updated_at"]


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "category", "mode", "status", "correct_count", "wrong_count", "created_at"]
    list_filter = ["mode", "status", "category"]
    readonly_fields = ["session_key", "created_at", "finished_at"]
    inlines = [SessionAnswerInline]

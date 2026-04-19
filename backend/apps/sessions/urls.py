from django.urls import path
from .views import (
    StartSessionView, SessionDetailView, SubmitAnswerView, SessionResultsView,
    TelegramUserUpsertView, TelegramUserBlockView,
)

urlpatterns = [
    path("sessions/", StartSessionView.as_view()),
    path("sessions/<uuid:session_key>/", SessionDetailView.as_view()),
    path("sessions/<uuid:session_key>/answer/", SubmitAnswerView.as_view()),
    path("sessions/<uuid:session_key>/results/", SessionResultsView.as_view()),
    path("tg-users/", TelegramUserUpsertView.as_view()),
    path("tg-users/<int:chat_id>/block/", TelegramUserBlockView.as_view()),
]

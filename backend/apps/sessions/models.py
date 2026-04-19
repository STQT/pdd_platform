import uuid
from django.db import models
from apps.questions.models import Category, Question, Answer


class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        name = self.first_name or ""
        if self.username:
            name += f" (@{self.username})"
        return f"{name} [{self.chat_id}]"


class TestSession(models.Model):
    MODE_TRAINING = "training"
    MODE_EXAM = "exam"
    MODE_CHOICES = [(MODE_TRAINING, "Training"), (MODE_EXAM, "Exam")]

    STATUS_ACTIVE = "active"
    STATUS_PASSED = "passed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PASSED, "Passed"),
        (STATUS_FAILED, "Failed"),
    ]

    session_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_TRAINING)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    question_ids = models.JSONField(default=list)  # ordered list of question PKs
    current_index = models.PositiveIntegerField(default=0)

    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session {self.session_key} [{self.status}]"

    @property
    def total(self):
        return len(self.question_ids)

    @property
    def answered(self):
        return self.correct_count + self.wrong_count


class SessionAnswer(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("session", "question")]
